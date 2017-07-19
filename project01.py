import sip
sip.setapi('QString', 2)
import sys

from xlrd import open_workbook
from PyQt4 import QtCore, QtGui



try:
    from PyQt4.phonon import Phonon
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "Music Player",
            # "Your Qt installation does not have Phonon support.",
            "La version de votre Qt ne supporte pas Phonon.",
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
            QtGui.QMessageBox.NoButton)
    sys.exit(1)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(QtGui.QMainWindow, self).__init__()

        self.setWindowIcon(QtGui.QIcon('logo.jpg'))   # definir l_icone

        self.audioOutput = Phonon.AudioOutput(
        	Phonon.MusicCategory, 
        	self
        )

        self.fichier_xlsx = "file01.xlsx"

        self.fichier_remote_dl = "" 
        self.fichier_sauve_local = ""

        self.list_fichier_dl = []
        # on va telechargee 1 aa 1 les fichier
        # # ceci va contenir le telechargement en cours 

        self.connect_sql_server()

        self.campagne = ""
        self.call_date = ""
        self.easycode = ""
        

        self.mediaObject = Phonon.MediaObject(self)
        self.metaInformationResolver = Phonon.MediaObject(self)
        self.mediaObject.setTickInterval(1000)
        self.mediaObject.tick.connect(self.tick)
        self.mediaObject.stateChanged.connect(self.stateChanged)
        self.metaInformationResolver.stateChanged.connect(self.metaStateChanged)
        self.mediaObject.currentSourceChanged.connect(self.sourceChanged)
        self.mediaObject.aboutToFinish.connect(self.aboutToFinish)

        Phonon.createPath(self.mediaObject, self.audioOutput)

        self.setupActions()

        ## #alternativo # si on veut afficher la barre des menus.. Decommenter la ligne_dessous
        self.setupMenus()
        self.setupUi()
        self.timeLcd.display("00:00") 

        self.sources = []

        ## point_important
        # tandremo am selection_

    def del01(self):
        self.qtlist_campagne.takeItem(1) 
        self.qtlist_campagne.addItem("cocococococococo")


    def sizeHint(self):
        return QtCore.QSize(1000, 300)

    def connect_sql_server(self, 
            server01 = '192.168.10.63',
            user01='easy',
            password01='e@sy1234',
            database01='AVR7'):
        """
        ceci ne devra etre executee qu_une seule fois
        - ceci est pour la connection aa la bdd
        """
        import _mssql
        self.conn_sql_server = _mssql.connect(
            server=server01, 
            user=user01, 
            password=password01, 
            database=database01)

        if self.conn_sql_server :
            print "connection ok!"
        else :
            print "connection au sql_server ECHOUEE"

    def extract01(self,
            query = ""):
        
        self.conn_sql_server \
            .execute_query('SELECT * FROM persons01 WHERE salesrep=%s', 'salesrep01')
        
        for row in self.conn_sql_server:
            print "ID=%d, Name=%s" % (row['id'], row['name'])

    def extraire_audio(self):
        print "t_as cliquee... operation extraction audio"

    def double_click_qtlist_easycode(self):
        self.campagne = self.combo_box__campagne.currentText()
        self.etat_comboS(
            campagne = False,
            call_date = False
            )
        req = "SELECT (time_stamp, 1, 4) "\
            +"+ '\\' + substring(time_stamp, 5, 2) "\
            +"+ '\\' + substring(time_stamp, 7, 2) "\
            +"+ '\\' + substring(time_stamp, 9, 2) "\
            +"+ '\\' + substring(time_stamp, 11, 2) "\
            +"+ '\\' + substring(time_stamp, 13, 2) "\
            +"+ rec_key + rec_time .codec FROM AVR7.dbo.recording WHERE "\
            +"CONVERT(varchar(8), time_stamp) = '" \
            + self.call_date \
            + "' AND rec_key in (SELECT easy.dbo.[call_thread].[recording_key] FROM " \
            + "easy.dbo."\
            +self.campagne\
            +" INNER JOIN easy.dbo.data_context ON easy.dbo.data_context.contact = easy.dbo." \
            + self.campagne \
            + ".easycode " \
            +"INNER JOIN easy.dbo.thread ON easy.dbo.thread.data_context = easy.dbo.data_context.code " \
            +"INNER JOIN easy.dbo.call_thread " \
            +"ON easy.dbo.thread.code = easy.dbo.call_thread.code " \
            +"WHERE easy.dbo."\
            +self.campagne \
            + ".easycode = "\
            +self.easycode + ")"

        print ""
        print ""
        print ""
        print ""
        print ""
        print "requete:"
        print req
        
        print ""

    def reinit_comboS(self):
        
        self.etat_comboS(
            campagne = True,
            call_date = False
            )
        
    def import_xls(self):
        """
        ceci va retourner le Chemin du fichier.xlsx qu_on veut ajouter
        """
        files = QtGui.QFileDialog.getOpenFileNames(self, "Veuillez choisir un Fichier Excel APPROPRIEE",
                QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.MusicLocation))

        if not files:
            return

        index = len(self.sources)

        if len (files) != 1:
            print "Vous avez choisit plusieurs fichiers... Veuillez choisir qu'une seule"
            QtGui.QMessageBox.information(
                self, 

                "Erreur d'Import de fichier", 
                "Erreur d'Import de fichier\n"
                "- Veuillez choisir qu'une seule fichier"
                )
            # raw_input("")
            sys.exit(0)

        
        # activer ceci si on accepte l_import de plusieurs fichiers
        # for string in files:    # string va contenir le chemin du fichier que t_as parcourue
        #     self.sources.append(Phonon.MediaSource(string)) # self.sources est une liste01.. afaik, il va contenir le playlist01
            # string va contenir le chemin du fichier que t_as parcourue
        #     print string

        self.fichier_xlsx = files
        print self.fichier_xlsx

            
    def addFiles(self):
        files = QtGui.QFileDialog.getOpenFileNames(self, 
            "Veuillez choisir un Fichier Audio",
            QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.MusicLocation))

        if not files:
            return

        index = len(self.sources)

        for string in files:
            self.sources.append(Phonon.MediaSource(string))
            
            

        if self.sources:
            self.metaInformationResolver.setCurrentSource(self.sources[index])

    def etat_comboS(self, 
            campagne = True,
            call_date = False):
        self.combo_box__campagne.setEnabled(campagne)

    


    










    def selection_change_combo_campagne(self):  
        print "changed combo box of campagne"
        self.etat_comboS(
            campagne = False,
            call_date = True
            )

        # print self.combo_box__campagne.currentText()

        list_call_date01 = \
            self.lire_xlsx__get_call_date(
                campgn = self.combo_box__campagne.currentText())

        print self.combo_box__campagne.currentText()
        print "#####################################"
        print list_call_date01
        list_call_date01 = list(set(list_call_date01))
        list_call_date01 = sorted(list_call_date01)
        
        
        # self.lire_xlsx__get_call_date(
            # campgn = str(
                # self.combo_box__campagne.currentText()
                # )
            # )

    def addFiles01(self):
        files = QtGui.QFileDialog.getOpenFileNames(self, "Veuillez choisir un Fichier Audio",
                QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.MusicLocation))

        if not files:
            return

        index = len(self.sources)

        res = ""
        for string in files:    # string va contenir le chemin du fichier que t_as parcourue
            self.sources.append(Phonon.MediaSource(string)) # self.sources est une liste01.. afaik, il va contenir le playlist01
            # string va contenir le chemin du fichier que t_as parcourue
            print string

            # il est possible de faire une chz comme la suivante
            # self.sources.append(Phonon.MediaSource(
            #         'E:\DISK_D\mamitiana\zik\Nouveau dossier\Embona(Donnah).mp3'
            #     )
            # )

        if self.sources:
            self.metaInformationResolver.setCurrentSource(self.sources[index])

    def click_play_audio(self):
        print "PLAY_audio si on clique"

    def lire_xls_csv(self):
        self.lire_xlsx()
        # print
        # print
        # print
        # print
        # print "#################################"
        # print
        # print
        # print
        # print
        # print
        # self.lire_csv()


    def lire_csv(self):
        import csv
        with open('resources.csv', 'rb') as csvfile:
            csv01 = csv.reader(
                csvfile, 
                delimiter=' ', 
                quotechar='|'
            )
            for row in csv01:
                print ', '.join(row)

    def lire_xlsx_campagne(
            self,
            fichier_xlsx = 'file01.xlsx'
        ):
        """
        ceci va retourner tout les list_campagnes qui sont sur le fichier.xlsx
        - list_campagnes sont d'abord trier PUIS supprimer_doublons
        """
        
        
        list_campagnes = []



        book = open_workbook(
            self.fichier_xlsx   # ce fichier doit etre inclus Apres clique du bouton__importer_action
                # pour le moment ceci n_est que pour le test
            ) 
        
        sheet0 = book.sheet_by_index(0) 

        # print sheet0.row_values(0, 1, 2)

        for i in range(2, sheet0.nrows):
            list_campagnes.append(
                sheet0.row_values(i, 0, 1)[0]
                )

        list_campagnes = list(set(list_campagnes))
        list_campagnes = sorted(list_campagnes)


        # print "liste campagne:"
        # print list_campagnes
        # print
        return list_campagnes
        


    def about(self):
        # QtGui.QMessageBox.information(self, "About Music Player",
        #         "The Music Player example shows how to use Phonon - the "
        #         "multimedia framework that comes with Qt - to create a "
        #         "simple music player.")
        QtGui.QMessageBox.information(
                self, 

                "Outil pour le Controle des Appels",

                "Outil pour le Controle des Appels\n"
                "- On choisit un fichier.xlsx\n"
                "- On choisit les champs (Campagne, Call_date, Easycode)\n"
                "- On clique sur bouton(Extraire) pour Telecharger les Audio correspondant\n"
                "- On choisit le fichier Audio qu'on veut lire\n"
                "- On clique sur bouton(Jouer) pour le mettre dans le Playlist"
                )

    def stateChanged(self, newState, oldState):
        if newState == Phonon.ErrorState:
            if self.mediaObject.errorType() == Phonon.FatalError:
                QtGui.QMessageBox.warning(self, "Fatal Error",
                        self.mediaObject.errorString())
            else:
                QtGui.QMessageBox.warning(self, "Error",
                        self.mediaObject.errorString())

        elif newState == Phonon.PlayingState:
            self.playAction.setEnabled(False)
            self.import_action.setEnabled(True)
            self.pauseAction.setEnabled(True)
            self.stopAction.setEnabled(True)

        elif newState == Phonon.StoppedState:
            self.stopAction.setEnabled(False)
            self.playAction.setEnabled(True)
            self.import_action.setEnabled(True)
            self.pauseAction.setEnabled(False)
            self.timeLcd.display("00:00")

        elif newState == Phonon.PausedState:
            self.pauseAction.setEnabled(False)
            self.stopAction.setEnabled(True)
            self.playAction.setEnabled(True)
            self.import_action.setEnabled(True)


    def tick(self, time):
        displayTime = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
        self.timeLcd.display(displayTime.toString('mm:ss'))

    def tableClicked(self, row, column):
        wasPlaying = (self.mediaObject.state() == Phonon.PlayingState)

        self.mediaObject.stop()
        self.mediaObject.clearQueue()

        self.mediaObject.setCurrentSource(self.sources[row])

        if wasPlaying:
            self.mediaObject.play()
        else:
            self.mediaObject.stop()

    def sourceChanged(self, source):    # afaik, ceci va s_exe si on a cliquee sur autre music dans play_list
        self.musicTable.selectRow(
            self.sources.index(source)
        )
        
        # ajouteed
        # self.musicTable02.selectRow(
        #     self.sources.index(source)
        # )

        self.timeLcd.display('00:00')
        # remote_file01 = "\\mcuci\\Storage$\\2017\\07\\05\\14\\03\\050003e0aa8c000001540595cf1976568001369720001000149.wav",

    def changed_campagne(self):
        print "changed campagne"

    def dl_fichier (
        self,
        bool01 = True,
        remote_file01 = "\\\\mcuci\\Storage$\\2017\\07\\05\\14\\03\\050003e0aa8c000001540595cf1976568001369720001000149.wav",
        sauvegardee_dans = ".\\ato100.wav"):

        print "clicked test"
        # sys.exit(0)
        import os
        import os.path
        if (os.path.exists(sauvegardee_dans)):
            print "fichier: " + sauvegardee_dans + " existe dans votre ordi"
            sys.exit(0)
        else:
            
            # mlam ... lasa nisi anlay param_bool01 io
                # print type (remote_file01)
                # print remote_file01
                # print type (sauvegardee_dans)
                # print sauvegardee_dans
            
            cmd01 = 'smbget '\
                + remote_file01\
                +' '\
                + sauvegardee_dans
            # sys.exit(0)
            os.system(cmd01)
            print "fichier: " \
                + remote_file01 \
                + " est sauvee dans "\
                + sauvegardee_dans

    def metaStateChanged(self, newState, oldState):
        if newState == Phonon.ErrorState:
            # QtGui.QMessageBox.warning(self, "Error opening files",
            QtGui.QMessageBox.warning(self, "Erreur sur l'ouverture du fichier",
                self.metaInformationResolver.errorString()
            )

            while self.sources and self.sources.pop() != self.metaInformationResolver.currentSource():
                pass

            return

        if \
            newState != Phonon.StoppedState \
            and \
            newState != Phonon.PausedState:
            return

        if self.metaInformationResolver.currentSource().type() == Phonon.MediaSource.Invalid:
            return

        metaData = self.metaInformationResolver.metaData()

        # title = metaData.get('TITLE', [''])[0]
        title = metaData.get('Titre', [''])[0]
        if not title:
            title = self.metaInformationResolver.currentSource().fileName()

        titleItem = QtGui.QTableWidgetItem(title)
        titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)

        # artist = metaData.get('ARTIST', [''])[0]
        artist = metaData.get('Titre01', [''])[0]
        artistItem = QtGui.QTableWidgetItem(artist)
        artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)

        # album = metaData.get('ALBUM', [''])[0]
        album = metaData.get('Titre02', [''])[0]
        albumItem = QtGui.QTableWidgetItem(album)
        albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)

        # year = metaData.get('DATE', [''])[0]
        year = metaData.get('Titre03', [''])[0]
        yearItem = QtGui.QTableWidgetItem(year)
        yearItem.setFlags(yearItem.flags() ^ QtCore.Qt.ItemIsEditable)

        currentRow = self.musicTable.rowCount()
        self.musicTable.insertRow(currentRow)
        self.musicTable.setItem(currentRow, 0, titleItem)
        self.musicTable.setItem(currentRow, 1, artistItem)
        self.musicTable.setItem(currentRow, 2, albumItem)
        self.musicTable.setItem(currentRow, 3, yearItem)

        # ajouteed
        # currentRow = self.musicTable.rowCount()
        # self.musicTable02.insertRow(currentRow)
        # self.musicTable02.setItem(currentRow, 0, titleItem)
        # self.musicTable02.setItem(currentRow, 1, artistItem)
        # self.musicTable02.setItem(currentRow, 2, albumItem)
        # self.musicTable02.setItem(currentRow, 3, yearItem)

        if not self.musicTable.selectedItems():
            self.musicTable.selectRow(0)
            self.mediaObject.setCurrentSource(self.metaInformationResolver.currentSource())

        # ajouteed
        # if not self.musicTable01.selectedItems():
        #     self.musicTable01.selectRow(0)
        #     self.mediaObject.setCurrentSource(self.metaInformationResolver.currentSource())


        source = self.metaInformationResolver.currentSource()
        index = self.sources.index(self.metaInformationResolver.currentSource()) + 1

        if len(self.sources) > index:
            self.metaInformationResolver.setCurrentSource(self.sources[index])
        else:
            self.musicTable.resizeColumnsToContents()
            if self.musicTable.columnWidth(0) > 300:
                self.musicTable.setColumnWidth(0, 300)


    def lire_xlsx__get_call_date(self, 
            fichier_xlsx = 'file01.xlsx',
            campgn = "0"):
        """
        va retourner les call_date qui sont reliees aa param_campgn
        """
        res_list_call_date = []

        print "get call_date"

        book = open_workbook(
            fichier_xlsx   # ce fichier doit etre inclus Apres clique du bouton__importer_action
                # pour le moment ceci n_est que pour le test
            ) 
        
        sheet0 = book.sheet_by_index(0) 

        for i in range(1, sheet0.nrows):
            if (sheet0.row_values(i, 0, 1)[0] == campgn):
                res_list_call_date.append(
                    sheet0.row_values(i, 1, 2)[0]
                )
            else:
                pass
        res_list_call_date 
        return res_list_call_date

    def click_extraire_audio(self):
        print "click extraire audio"

    def aboutToFinish(self):
        index = self.sources.index(self.mediaObject.currentSource()) + 1
        if len(self.sources) > index:
            self.mediaObject.enqueue(self.sources[index])

    def setupActions(self):
        self.playAction = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_MediaPlay), 
            "Play",
            self, 
            shortcut="Ctrl+P", 
            enabled=False,
            triggered=self.mediaObject.play
        )


        self.import_action = QtGui.QAction(
            "Importer",
            self, 
            shortcut="Ctrl+I", 
            enabled=True,
            triggered=self.import_xls
        )

        # self.bouton_extraire_audio = QtGui.QAction(
        #     "Importer",
        #     self, 
        #     shortcut="Ctrl+P", 
        #     enabled=True,
        #     triggered=self.extraire_audio
        # )

        self.bouton_extraire_audio = QtGui.QPushButton(
            "Extraire"
        )
        self.bouton_reinit_comboS = QtGui.QPushButton(
            "Reinitialiser"
        )

        self.bouton_test = QtGui.QPushButton(
            "Test"
        )

        # self.bouton_extraire_audio.clicked.connect(self.click_extraire_audio)
        self.bouton_extraire_audio.clicked.connect(self.lire_xls_csv)
        self.bouton_reinit_comboS.clicked.connect(
            self.reinit_comboS
            # (
                # text01 = "akondro"
            # )
        )
        self.bouton_test.clicked.connect(
            # self.dl_fichier ## bouton_test_dl
            # self.select_fichier_dl
            self.del01
        )

        self.bouton_play_audio = QtGui.QPushButton(
            "Jouer"
        )

        self.bouton_play_audio.clicked.connect(self.click_play_audio)

        self.pauseAction = QtGui.QAction(
            self.style().standardIcon(
            	QtGui.QStyle.SP_MediaPause
            ),
            "Pause", self, shortcut="Ctrl+A", enabled=False,
            triggered=self.mediaObject.pause
        )

        self.stopAction = QtGui.QAction(
                self.style().standardIcon(
                	QtGui.QStyle.SP_MediaStop
                ), 
                "Stop",
                self, shortcut="Ctrl+S", enabled=False,
                triggered=self.mediaObject.stop)

        self.nextAction = QtGui.QAction(
                self.style().standardIcon(
                    QtGui.QStyle.SP_MediaSkipForward
                ),
                "Next", 
                self, 
                shortcut="Ctrl+N"
        )

        self.previousAction = QtGui.QAction(
                self.style().standardIcon(
                    QtGui.QStyle.SP_MediaSkipBackward
                ),
                "Previous", self, shortcut="Ctrl+R")

        self.addFilesAction = QtGui.QAction(
                "Ajouter un &Fichier", 
                self,
                shortcut="Ctrl+F", 
                triggered=self.addFiles
        )

        self.exitAction = QtGui.QAction(
            "E&xit", 
            self, 
            shortcut="Ctrl+X",
            triggered=self.close
        )

        self.aboutAction = QtGui.QAction(
            "A&bout", 
            self, 
            shortcut="Ctrl+B",
            triggered=self.about
        )

        self.aboutQtAction = QtGui.QAction(
            "A propos de &Qt", 
            self,
            shortcut="Ctrl+Q", 
            triggered=QtGui.qApp.aboutQt
        )

    def method01(self):
        print "this is a test"

    def setupMenus(self):
        # fileMenu = self.menuBar().addMenu("&File")
        fileMenu = self.menuBar().addMenu("&Fichier")
        fileMenu.addAction(self.addFilesAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        # aboutMenu = self.menuBar().addMenu("&Help")
        aboutMenu = self.menuBar().addMenu("&Aide")
        aboutMenu.addAction(self.aboutAction)
        aboutMenu.addAction(self.aboutQtAction)

    def setupUi(self):
        bar = QtGui.QToolBar()
        qtool_bar02 = QtGui.QToolBar()

        bar.addAction(self.playAction)
        bar.addAction(self.pauseAction)
        bar.addAction(self.stopAction)
        qtool_bar02.addAction(self.import_action)
        

        self.seekSlider = Phonon.SeekSlider(self)
        self.seekSlider.setMediaObject(self.mediaObject)

        self.volumeSlider = Phonon.VolumeSlider(self)
        self.volumeSlider.setAudioOutput(self.audioOutput)
        self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum,
                QtGui.QSizePolicy.Maximum)

        volumeLabel = QtGui.QLabel()
        volumeLabel.setPixmap(QtGui.QPixmap('images/volume.png'))

        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Light, QtCore.Qt.darkGray)

        self.timeLcd = QtGui.QLCDNumber()
        self.timeLcd.setPalette(palette)

        headers = ("Title", "Artist", "Album", "Year")
        # headers = ("Title", "Titre01", "Titre02", "Titre03")

        self.musicTable = QtGui.QTableWidget(0, 4)
        self.musicTable01 = QtGui.QTableWidget(0, 4)
        self.musicTable02 = QtGui.QTableWidget(0, 4)

        self.musicTable01.setItem(0,0, QtGui.QTableWidgetItem("Item (1,1)"))
        self.musicTable01.setItem(0,1, QtGui.QTableWidgetItem("Item (1,2)"))
        self.musicTable01.setItem(1,0, QtGui.QTableWidgetItem("Item (2,1)"))
        self.musicTable01.setItem(1,1, QtGui.QTableWidgetItem("Item (2,2)"))
        self.musicTable01.setItem(2,0, QtGui.QTableWidgetItem("Item (3,1)"))
        self.musicTable01.setItem(2,1, QtGui.QTableWidgetItem("Item (3,2)"))
        self.musicTable01.setItem(3,0, QtGui.QTableWidgetItem("Item (4,1)"))
        self.musicTable01.setItem(3,1, QtGui.QTableWidgetItem("Item (4,2)"))
        self.musicTable01.show()
        
        self.combo_box__campagne = QtGui.QComboBox()

        self.qtlist_campagne = QtGui.QListWidget()
        self.qtlist_campagne.addItem("campagne01")
        self.qtlist_campagne.addItem("campagne02")
        self.qtlist_campagne.addItem("campagne03")
        self.qtlist_campagne.addItem("campagne04")
        self.qtlist_campagne.addItem("campagne05")
        self.qtlist_campagne.addItem("campagne06")
        self.qtlist_campagne.addItem("campagne07")
        self.qtlist_campagne.addItem("campagne08")
        self.qtlist_campagne.addItem("campagne09")
        self.qtlist_campagne.addItem("campagne10")
        self.qtlist_campagne.addItem("campagne11")
       

        self.qtlist_campagne.\
            currentItemChanged.\
            connect(self.changed_campagne)
        
        self.combo_box__campagne.addItems(
            # ["campagne01", "campagne02", "campagne03"]
            self.lire_xlsx_campagne()
        )
        self.combo_box__campagne.\
            currentIndexChanged.\
            connect(
                self.selection_change_combo_campagne
            )

        
        self.combo_box__campagne.setStyleSheet('''
            QComboBox { max-width: 100px; min-height: 20px;}
            '''    
            )


        



        # etat des self.(
        #    combo_box__campagne)
        # # au temps = 0
        self.combo_box__campagne.setEnabled(True)
        

        self.musicTable.setHorizontalHeaderLabels(headers)
        self.musicTable.setSelectionMode(
            QtGui.QAbstractItemView.SingleSelection
        )
        self.musicTable01.setHorizontalHeaderLabels(headers)
        self.musicTable01.setSelectionMode(
            QtGui.QAbstractItemView.SingleSelection
        )
        self.musicTable02.setHorizontalHeaderLabels(headers)
        self.musicTable02.setSelectionMode(
            QtGui.QAbstractItemView.SingleSelection
        )

        self.musicTable.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows
        )

        self.musicTable.cellPressed.connect(
            self.tableClicked
        )

        seekerLayout = QtGui.QHBoxLayout()
        seekerLayout.addWidget(
            self.seekSlider
        )

        seekerLayout.addWidget(
            self.timeLcd
        )

        playbackLayout = QtGui.QHBoxLayout()
        qhboxlayout_toolbar_play = QtGui.QHBoxLayout()
        playbackLayout.addWidget(bar)
        qhboxlayout_toolbar_play.addWidget(qtool_bar02)

        playbackLayout.addStretch()
        playbackLayout.addWidget(
            volumeLabel
        )

        playbackLayout.addWidget(
            self.volumeSlider
        )




        mainLayout = QtGui.QVBoxLayout()
        qvbox_layout_music_table01 = QtGui.QHBoxLayout()
        qvbox_layout_music_table02 = QtGui.QHBoxLayout()


        qvbox_layout_music_table01.addWidget(self.combo_box__campagne)
        qvbox_layout_music_table01.addWidget(self.qtlist_campagne)
        qvbox_layout_music_table01.addWidget(self.musicTable01)
        qvbox_layout_music_table01.addWidget(self.bouton_extraire_audio)
        qvbox_layout_music_table01.addWidget(self.bouton_reinit_comboS)

        qvbox_layout_music_table02.addWidget(self.musicTable02)
        qvbox_layout_music_table02.addWidget(self.bouton_test)
        qvbox_layout_music_table02.addWidget(self.bouton_play_audio)


        mainLayout.addWidget(
            self.musicTable
        )

        mainLayout.addLayout(
            seekerLayout
        )

        mainLayout.addLayout(
            playbackLayout
        )

        mainLayout.addLayout(
            qhboxlayout_toolbar_play
        )  

        mainLayout.addLayout(
            qvbox_layout_music_table01
        )

              

        mainLayout.addLayout(
            qvbox_layout_music_table02
        )

        widget = QtGui.QWidget()
        widget.setLayout(
            mainLayout
        )

        self.setCentralWidget(
            widget
        )

        self.setWindowTitle(
            "Vivetic"
        )







app = QtGui.QApplication(sys.argv)
app.setApplicationName("Music Player")
app.setQuitOnLastWindowClosed(True)
app.setWindowIcon(QtGui.QIcon('Py.ico'))

window = MainWindow()

if __name__ == '__main__':
    
    window.show()

    sys.exit(app.exec_())