import sip
sip.setapi('QString', 2)
import sys
import os
import os.path
from subprocess import check_output
import psycopg2

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

        self.connect_sql_server()
        self.connect_pg()

        self.campagne = ""
        self.call_date = ""
        self.multieasycode = ""

        self.list_monoeasycode = []


        

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
        self.etat_elemS(
            campg = True,
            multieasyc = True,
            monoeasyc = True,
            dldd = True
        )
        self.timeLcd.display("00:00") 

        self.sources = []

    def clicked_play_action(self):
        self.mediaObject.play()
        print "you clicked play_button"

    def etat_elemS(self,
            campg = False,
            multieasyc = False,
            monoeasyc = False,
            dldd = False):
        self.combo_box__campagne.setEnabled(campg)
        self.qtlist_multieasycode.setEnabled(multieasyc)
        
        self.qtlist_dldd.setEnabled(dldd)
        print ""

    def umount_samba_server(self):
        from subprocess import Popen
        Popen("bat_files\\umount_samba_voice.bat")
        print "unmounted samba_voice "
        Popen("bat_files\\umount_samba_Storage.bat")
        print "unmounted samba_Storage"
        
    def double_clicked_qtable01(self):
        print "double clicked potato" 
        
        self.sources.append(Phonon.MediaSource(
            "E:\DISK_D\mamitiana\zik\Nouveau dossier\Rabl - Ra fitia.mp3"
            ))


            
        index = len(self.sources)
        print "index: " + str(index)
        if self.sources:
            self.metaInformationResolver.setCurrentSource(self.sources[index - 1])

        

    def mount_samba_server(self):
        '''
        Ny "voice" dia montena ao am V:
        Ny "Storage" dia montena ao am S:
        '''
        from subprocess import Popen
        Popen("bat_files\\mount_samba_voice.bat")
        print "samba_voice mounted"
        Popen("bat_files\\mount_samba_Storage.bat")
        print "samba_Storage mounted"
        print "mount samba server"



    def double_clicked_multieasycode(self):
        print "double clicked multieasycode"
        print "- mande manao anlay requete lava b amzai"
        print ""
        print ""
        print ""
        print ""
        print ""
        self.campagne = self.combo_box__campagne.currentText()
        self.multieasycode = self.qtlist_multieasycode.\
            currentItem().\
            text()


        # dans double_clicked_multieasycode
        ##requete ##query
        req = "SELECT substring(time_stamp, 1, 4) "\
            +"+ '\\' + substring(time_stamp, 5, 2) "\
            +"+ '\\' + substring(time_stamp, 7, 2) "\
            +"+ '\\' + substring(time_stamp, 9, 2) "\
            +"+ '\\' + substring(time_stamp, 11, 2) "\
            +"+ '\\' + substring(time_stamp, 13, 5) "\
            +"+ rec_key + rec_time +'.'+codec as chemin FROM AVR7.dbo.recording WHERE "\
            +"rec_key in (SELECT easy.dbo.[call_thread].[recording_key] FROM " \
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
            +self.multieasycode +")"

        print ""
        print ""
        print ""
        print ""
        print ""
        print "requete dans double_clicked_multieasycode:"
        print req
        


        
        
        self.conn_sql_server \
            .execute_query(req)

        print ""
        print ""
        print ""
        print ""
        print ""
        print ""

        # dans double_clicked_multieasycode
        
        for row in self.conn_sql_server:
            
            self.list_monoeasycode.\
                append(row['chemin'])

        # esorina ni doublon ari triena
        self.list_monoeasycode = list(set(self.list_monoeasycode))
        self.list_monoeasycode = sorted(self.list_monoeasycode)

        print self.list_monoeasycode
        
        # mameno anlay qtlist_monoeasycode   
        # elem01... io no chemin ani am server
        # # io mbola tsisy racine
        # # ex: 2017\\06\\23\\12\\05\\460003e0aa8c000001540594d04022591000f86e60001000003.wav
        for elem01 in self.list_monoeasycode:
            self.qtlist_monoeasycode.\
                addItem(elem01)
        

        # fin double_clicked_multieasycode





    def sizeHint(self):
        return QtCore.QSize(1000, 500)



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
            print "connection ok au sql_server!"
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
        
        req = "SELECT (time_stamp, 1, 4) "\
            +"+ '\\' + substring(time_stamp, 5, 2) "\
            +"+ '\\' + substring(time_stamp, 7, 2) "\
            +"+ '\\' + substring(time_stamp, 9, 2) "\
            +"+ '\\' + substring(time_stamp, 11, 2) "\
            +"+ '\\' + substring(time_stamp, 13, 2) "\
            +"+ rec_key + rec_time .codec FROM AVR7.dbo.recording WHERE "\
            +"rec_key in (SELECT easy.dbo.[call_thread].[recording_key] FROM " \
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


        
    def msg_box_information(self, titre, txt):
        QtGui.QMessageBox.information(
                self, 
                titre, 
                txt
                )


    def select_chemin(self,
            bool01 = True,
            campagne = "CT_NOMINATION_AS3",
            multieasy = "17868031"):
        req = "SELECT substring(time_stamp, 1, 4) "\
            +"+ '\\' + substring(time_stamp, 5, 2) "\
            +"+ '\\' + substring(time_stamp, 7, 2) "\
            +"+ '\\' + substring(time_stamp, 9, 2) "\
            +"+ '\\' + substring(time_stamp, 11, 2) "\
            +"+ '\\' + substring(time_stamp, 13, 5) "\
            +"+ rec_key + rec_time +'.'+codec as chemin FROM AVR7.dbo.recording WHERE "\
            +"rec_key in (SELECT easy.dbo.[call_thread].[recording_key] FROM " \
            + "easy.dbo."\
            +campagne\
            +" INNER JOIN easy.dbo.data_context ON easy.dbo.data_context.contact = easy.dbo." \
            + campagne \
            + ".easycode " \
            +"INNER JOIN easy.dbo.thread ON easy.dbo.thread.data_context = easy.dbo.data_context.code " \
            +"INNER JOIN easy.dbo.call_thread " \
            +"ON easy.dbo.thread.code = easy.dbo.call_thread.code " \
            +"WHERE easy.dbo."\
            +campagne \
            + ".easycode = "\
            +str(multieasy) +")"

        print req

        print ""
        print ""
        print ""
        print "requete dans meth__select_chemin : "
        print req
        self.conn_sql_server \
            .execute_query(req)

        #dans select_chemin

        plusieurs_monoeasy = []
        for row in self.conn_sql_server:
            plusieurs_monoeasy.\
                append(row['chemin'])

        return plusieurs_monoeasy
        #fin select_chemin



    def import_xls(self,
            bool01 = True,
            root_local = "E:\\DISK_D\\ecoutes", 
            root_distant = "\\\\mcuci\\Storage$\\",
            telechargee = "0",
            fini = "0",
            monoeasy = "17868031"
        ):
        """
        ceci va retourner le Chemin du fichier.xlsx qu_on veut ajouter
        """
        
        self.remove_all_qtlist_multieasycode()
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


        tmp = files[0]
        if tmp[-5:] == ".xlsx":
            self.fichier_xlsx = tmp
            print "fichier_xlsx: " + self.fichier_xlsx
        else:
            self.msg_box_information(
                "ERREUR de Fichier",
                "Votre fichier n'est pas un fichier excel CONVENABLE")

        # self.lire_xlsx_campagne(
            # fichier_xlsx = self.fichier_xlsx)

        self.etat_elemS(
            campg = True,
            multieasyc = True,
            monoeasyc = True,
            dldd = True
        )

        book = open_workbook(
            self.fichier_xlsx   
        )

        cheminS = self.select_chemin(
            campagne = "CT_NOMINATION_AS3",
            multieasy = "17868031"
            );


        
        # sys.exit(0)


        query_insert = "INSERT INTO " \
            + "prj_ecoute01 "\
            +"(chemin__a_partir_root, "\
            +"root_local, root_distant, "\
            +"telechargee, fini, multi_easycode) " +\
            "VALUES " 
            

        #dans import_xls
        sheet0 = book.sheet_by_index(0)
        list_multieasycode = []
        for i in range(0, sheet0.nrows):
            multieasyc_i = sheet0.row_values(i, 0, 1)[0]
            cheminS = self.select_chemin(
                    campagne = "CT_NOMINATION_AS3",
                    multieasy = multieasyc_i
                    );

            if i != (sheet0.nrows-1):
                cpt_chm = 0
                for chemin in cheminS:
                    if cpt_chm != (len(cheminS) - 1):
                        query_insert += "( '"
                        query_insert += chemin + "', '" \
                        + root_local + "', '"\
                        + root_distant + "', '"\
                        + telechargee + "', '"\
                        + fini + "', "\
                        + str(int(multieasyc_i)) + "), "
                    else:
                        query_insert += "( '"
                        query_insert += chemin + "', '" \
                        + root_local + "', '"\
                        + root_distant + "', '"\
                        + telechargee + "', '"\
                        + fini + "', "\
                        + str(int(multieasyc_i)) + "), "
                    cpt_chm = cpt_chm + 1

                print ""
                print ""
                print ""
                print ""
                print ""
                print "query_insert dans import_xls __code__0001: " + query_insert


                list_multieasycode.append(
                    multieasyc_i
                    )
            else:

                cpt_chm = 0
                for chemin in cheminS:
                    if cpt_chm != (len(cheminS) - 1):
                        query_insert += "( '"
                        query_insert += chemin + "', '" \
                        + root_local + "', '"\
                        + root_distant + "', '"\
                        + telechargee + "', '"\
                        + fini + "', "\
                        + str(int(multieasyc_i)) + "), "
                    else:
                        query_insert += "( '"
                        query_insert += chemin + "', '" \
                        + root_local + "', '"\
                        + root_distant + "', '"\
                        + telechargee + "', '"\
                        + fini + "', "\
                        + str(int(multieasyc_i)) + ") "
                    cpt_chm = cpt_chm + 1

                print ""
                print ""
                print ""
                print ""
                print ""
                print "query_insert dans import_xls __code__0001: " + query_insert

                list_multieasycode.append(
                    multieasyc_i
                    )


        print "query_insert dans import_xls __code002__: " + query_insert
        self.cursor_pg.execute(query_insert)


        self.connect_pg.commit()

        # self.conn_sql_server \
            # .execute_query(query_insert)

        #dans import_xls
        # on elimine les doublons
        list_multieasycode = list(
            set(
                list_multieasycode
            )
        )

        # on fait un tri
        list_multieasycode = sorted(list_multieasycode)



        print ""
        print ""
        print ""
        print ""
        print ""
        # print list_multieasycode
        
        # elem sera un mono_easycode
        for elem in list_multieasycode:
            if (str(elem)[-2:] == ".0"):
                self.qtlist_multieasycode.\
                    addItem(str(elem)[:-2])
            else:
                self.qtlist_multieasycode.\
                    addItem(str(elem))

        
        ######eto
        # ao am meth__import_xls
        # # manao ajout ani anaty table(prj_ecoute01) fona ni appli refa
        # # manao import_fichier.xlsx
        # #
        # #
        # # atov we
        # # # mnw test ani am table loon.... ka rah tsy ao ni easycode01
        # # # amzai vao mnw insertion any anaty table(prj_ecoute01)



        #fin_import_xls



    def check_existance_pg(self, 
            bool01 = True, 
            table01 = "prj_ecoute01", 
            chp01 = "chemin__a_partir_root",
            val = ' 2017\\06\\23\\12\\05\\460003e0aa8c000001540594d04022591000f86e60001000003.wav'):
        req = "SELECT EXISTS" \
            + "(SELECT * FROM " \
            + table01 \
            + " WHERE " \
            + chp01 \
            + " = '"\
            + val \
            + "');"
        self.cursor_pg.execute(req)
        rows = self.cursor_pg.fetchall()
        print rows
        if len(rows) != 0:
            return True
        else:
            return False

    def pg_insert(self, query):
        self.cursor_pg.execute(query)
        self.connect_pg.commit()

    def connect_pg(self, 
            server01 = '127.0.0.1',
            user01='postgres',
            password01='123456',
            database01='saisie'):

        self.connect_pg = psycopg2.connect(
            "dbname=" + database01
            +" user=" + user01
            +" password=" + password01
            +" host=" + server01
        ) #local

        self.connect_pg.set_isolation_level(0)

        self.cursor_pg = self.connect_pg.cursor()

        print "connection ok au postgresql"

     
            
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


    


    










    def selection_change_combo_campagne(self):  
        print "changed combo box of campagne"
        

        # print self.combo_box__campagne.currentText()

        list_call_date01 = \
            self.lire_xlsx__get_call_date(
                campgn = self.combo_box__campagne.currentText())

        self.etat_elemS(
            campg = False,
            multieasyc = True,
            monoeasyc = False,
            dldd = True
        )

        print self.combo_box__campagne.currentText()
        print "#####################################"
        print list_call_date01
        list_call_date01 = list(set(list_call_date01))
        list_call_date01 = sorted(list_call_date01)

        # print list_call_date01
        for a in list_call_date01 :
            if (str(a)[-2:] == ".0"):
                self.qtlist_multieasycode.\
                    addItem(str(a)[:-2])
            else:
                self.qtlist_multieasycode.\
                    addItem(str(a))




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


        
                


    def lire_xls_csv(self):
        self.campagne = self.combo_box__campagne\
            .currentItem()\
            .text()
        print ""


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
        print list_campagnes
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
        self.timeLcd.display('00:00')
        

    def samba_check_file(self,
            bool01 = True,  # franchement tsy haiko ni dikanito.. misi anio bool01 io maro2 aah
            samba_server_storage = "\\\\mcuci\\Storage$",
            remote_file = "\\2017\\07\\05\\14\\03\\050003e0aa8c000001540595cf1976568001369720001000149.wav"):
        from pathlib import Path
        
        path_to_file = samba_server_storage + remote_file

        # testena ao am storage
        my_file = Path(path_to_file)
        if my_file.is_file():
            print "ao am storage"
        else:
            samba_server_voice = "\\\\192.168.10.19\\voice"
            path_to_file = samba_server_voice + remote_file
            my_file = Path(path_to_file)
            if my_file.is_file():
                print "ao am voice"
            else:
                print "fichier inexistant"


        return my_file.is_file()

        # os.system()


        print ""


    def changed_campagne(self):
        print "changed campagne"

    def dl_fichier (
        self,
        bool01 = True,
        remote_file01 = "\\\\mcuci\\Storage$\\2017\\07\\05\\14\\03\\050003e0aa8c000001540595cf1976568001369720001000149.wav",
        sauvegardee_dans = ".\\ato100.wav"):

        print "clicked test"
        # sys.exit(0)
        
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

    def remove_all_qtlist_multieasycode(self):
        # print self.qtlist_multieasycode.count()
        for i in xrange(self.qtlist_multieasycode.count()):
            # ne comprend pas pourquoi si on fait qu_une seule fois
            # # la prochaine_ligne, alors on va supprimer que la moitiee
            self.qtlist_multieasycode.takeItem(i)
            self.qtlist_multieasycode.takeItem(i)
            self.qtlist_multieasycode.takeItem(i)
            self.qtlist_multieasycode.takeItem(i)
            self.qtlist_multieasycode.takeItem(i)
            self.qtlist_multieasycode.takeItem(i)



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
            # triggered=self.mediaObject.play
            triggered=self.clicked_play_action
        )


        self.import_action = QtGui.QAction(
            "Importer",
            self, 
            shortcut="Ctrl+I", 
            enabled=True,
            triggered=self.import_xls
        )



        self.bouton_reinit_elemS = QtGui.QPushButton(
            "Reinitialiser"
        )

        self.bouton_test = QtGui.QPushButton(
            "Test"
        )

        self.bouton_reinit_elemS.clicked.connect(
            self.remove_all_qtlist_multieasycode
            # (
                # text01 = "akondro"
            # )
        )
        self.bouton_test.clicked.connect(
            # self.dl_fichier ## bouton_test_dl
            # self.select_fichier_dl
            # self.remove_all_qtlist_multieasycode
            # self.samba_check_file
            # self.extract01  # that one is going to extract some BASIC info from sql_server
                            # # you should delete that one
            # self.umount_samba_server
            # self.lire_xlsx_campagne 
            self.dialog_monoeasycode
            # self.check_existance_pg
        )

        self.bouton_play_audio = QtGui.QPushButton(
            "Jouer"
        )

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


    def dialog_monoeasycode(self, 
            bool01 = True,
            list__dl_fini_chemin_easycode
            = 
            [
                [False, True, 'chemin01', 'easycode01'],
                [True, False, 'chemin02', 'easycode02'],
                [True, False, 'chemin03', 'easycode03'],
                [False, True, 'chemin04', 'easycode04'],
                [True, True, 'chemin05', 'easycode05'],
            ]
        ):

        # misi requete insertion

        # misi requete update

        # #instanciation inside dialog
        dialog01 = QtGui.QDialog()
        qvbox_layout_dialog = QtGui.QHBoxLayout(dialog01)
        
        button01 = QtGui.QPushButton("ok", dialog01)


        rows = len(list__dl_fini_chemin_easycode)
        cols = len(list__dl_fini_chemin_easycode[0])
        self.qtable01 = QtGui.QTableWidget(rows, cols, dialog01)
        self.qtable01.setSelectionBehavior(QtGui.QTableView.SelectRows);

        dialog01.setMinimumSize(600, 50)
        self.qtable01.setStyleSheet(
            '''
            QTableWidget { max-width: 600px; min-height: 200px;}
            '''
            )
        qvbox_layout_dialog.addWidget(button01)
        qvbox_layout_dialog.addWidget(self.qtable01)

        # les entetes du table_dialog
        self.qtable01.setHorizontalHeaderLabels(
            ['Download', 'Fini', 'Chemin', 'Easycode'])

        self.qtable01.doubleClicked.connect(self.double_clicked_qtable01)

        for row in range(len(list__dl_fini_chemin_easycode)):
            for col in range(len(list__dl_fini_chemin_easycode[row])):
                
                if col == 0:
                    # Download
                    item = QtGui.QTableWidgetItem('')
                    if(list__dl_fini_chemin_easycode[row][col] == False):
                        item.setCheckState(QtCore.Qt.Unchecked)
                        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    else:
                        item.setCheckState(QtCore.Qt.Checked)
                        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    self.qtable01.setItem(row, col, item)

                elif col == 1:
                    # Fini
                    item = QtGui.QTableWidgetItem()
                    if(list__dl_fini_chemin_easycode[row][col] == False):
                        item.setCheckState(QtCore.Qt.Unchecked)
                        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    else:
                        item.setCheckState(QtCore.Qt.Checked)
                        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    
                    self.qtable01.setItem(row, col, item)

                elif col == 2:
                    # Chemin
                    item = QtGui.QTableWidgetItem(
                        list__dl_fini_chemin_easycode[row][col]
                    )
                    # item.setCheckState(QtCore.Qt.Unchecked)
                    self.qtable01.setItem(row, col, item)
                elif col == 3:
                    item = QtGui.QTableWidgetItem(
                        list__dl_fini_chemin_easycode[row][col]
                    )
                    self.qtable01.setItem(row, col, item)


        dialog01.setWindowTitle("Dialog")
        dialog01.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog01.exec_()

    def clicked_button_dialog(self):
        print "clicked button inside dialog"



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


        


        #~ #instanciation by default

        self.musicTable = QtGui.QTableWidget(0, 4)
        
        
        self.combo_box__campagne = QtGui.QComboBox()

        self.qtlist_dldd = QtGui.QListWidget()
        

        self.qtlist_multieasycode = QtGui.QListWidget()
        self.qtlist_multieasycode.setStyleSheet('''
            QListWidget { max-width: 150px; min-height: 200px;}
            '''
            )

        self.qtlist_multieasycode.addItem("")

        self.qtlist_monoeasycode = QtGui.QListWidget()
        

        self.combo_box__campagne.setStyleSheet('''
            QComboBox { max-width: 100px; min-height: 20px;}
            '''
            )



        self.combo_box__campagne.addItems(
            # ["campagne01", "campagne02", "campagne03"]
            self.lire_xlsx_campagne()
        )

        #~ ##liaison des elem_graphique avec meth01
        self.combo_box__campagne.\
            currentIndexChanged.\
            connect(
                self.selection_change_combo_campagne
            )




        
        self.qtlist_multieasycode.\
            itemDoubleClicked.\
            connect(self.double_clicked_multieasycode)

        


        



        # etat des self.(
        #    combo_box__campagne)
        # # au temps = 0
        self.combo_box__campagne.setEnabled(True)
        

        self.musicTable.setHorizontalHeaderLabels(headers)
        self.musicTable.setSelectionMode(
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
        qvbox_layout_music_table01.addWidget(self.qtlist_multieasycode)
        # qvbox_layout_music_table01.addWidget(self.qtlist_monoeasycode)
        qvbox_layout_music_table01.addWidget(self.bouton_reinit_elemS)

        qvbox_layout_music_table02.addWidget(self.qtlist_dldd)
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