import sip
sip.setapi('QString', 2)
import sys
import os
import os.path
import time
from subprocess import check_output
import psycopg2
from pathlib import Path

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
        
        # ti mbl mnw telechargement FTSN
        # mnw requete ani am pg we aiza no misi anlay 
        # # full_path_read
        # #
        # # arakaraka ni self.clicked_enreg


        
        
 
        index = len(self.sources)
        print "index: " + str(index)
        if self.sources:
            self.metaInformationResolver.setCurrentSource(self.sources[index - 1])

        indexes = self.qtable01.selectionModel().selectedRows()

        print "index024689361: " 

        print indexes
        for index in sorted(indexes):
            print('Row %d is selected' % index.row())
            self.clicked_enreg = self.\
                list__dl_fini_chemin_easycode[index.row()][2]
            print self.list__dl_fini_chemin_easycode[index.row()][2]
        ######eto
        # rhf m_click anlay item ao am item@qtable01 dia 
        # # m_dl
        # # # testena loon we aiz no misi anlay fichier tkn dl_na
        # # # sauvena qlq_part ilai fichier__n_telechargena
        # # # alefa ani am self.source ilai fichier__n_telechargena
        # # manao anlai play ao am n_telechargena
        req = "SELECT"\
            +" root_distant, chemin__a_partir_root "\
            +"FROM prj_ecoute01 "\
            +"WHERE "\
            +"chemin__a_partir_root "\
            +"= '"\
            +self.clicked_enreg\
            +"';"
        print req

        self.pg_select(
            query = req
            )

        self.full_path_read = ""
        print "pg_select 534546546978"
        for row in self.rows_pg:
            for i in range(len(row)):
                if i == 1:
                    self.chemin_sans_root = row[i]
                self.full_path_read = \
                    self.full_path_read + row[i]

        # sys.exit(0)
        print "full_path: "
        print self.full_path_read

        print ""
        print ""
        print ""
        print self.root_local + self.chemin_sans_root
        # sys.exit(0)
        self.dl_fichier(
            remote_file01 = self.full_path_read,
            sauvegardee_dans = self.root_local + str(self.chemin_sans_root)[-55:]
            )

        time.sleep(2)
        self.sources.append(Phonon.MediaSource(
            self.root_local + str(self.chemin_sans_root)[-55:]
            ))


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


    # attention au 
    def pg_select(self,
            query = "select * from prj_ecoute01"):
        self.cursor_pg.execute(query)
        self.rows_pg = self.cursor_pg.fetchall()

        print "pg_select _ code 000012654564"


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
        # ti requete ti dia hnw requete ani am sql_server
            # req = "SELECT substring(time_stamp, 1, 4) "\
                # +"+ '\\' + substring(time_stamp, 5, 2) "\
                # +"+ '\\' + substring(time_stamp, 7, 2) "\
                # +"+ '\\' + substring(time_stamp, 9, 2) "\
                # +"+ '\\' + substring(time_stamp, 11, 2) "\
                # +"+ '\\' + substring(time_stamp, 13, 5) "\
                # +"+ rec_key + rec_time +'.'+codec as chemin FROM AVR7.dbo.recording WHERE "\
                # +"rec_key in (SELECT easy.dbo.[call_thread].[recording_key] FROM " \
                # + "easy.dbo."\
                # +self.campagne\
                # +" INNER JOIN easy.dbo.data_context ON easy.dbo.data_context.contact = easy.dbo." \
                # + self.campagne \
                # + ".easycode " \
                # +"INNER JOIN easy.dbo.thread ON easy.dbo.thread.data_context = easy.dbo.data_context.code " \
                # +"INNER JOIN easy.dbo.call_thread " \
                # +"ON easy.dbo.thread.code = easy.dbo.call_thread.code " \
                # +"WHERE easy.dbo."\
                # +self.campagne \
                # + ".easycode = "\
                # +self.multieasycode +")"

        # alaina aa partir ny: multieasycode, table_campagne
        req = "SELECT " \
        + "telechargee, " \
        + "fini, " \
        + "chemin__a_partir_root, " \
        + "multi_easycode " \
        + "root_local, " \
        + "root_distant " \
        + "FROM prj_ecoute01 " \
        + "WHERE table_campagne like '" \
        + self.combo_box__campagne.currentText() \
        + "' AND " + "multi_easycode=" \
        + self.qtlist_multieasycode.currentItem().text()

        print "code654654654654: " 
        print type(self.qtlist_multieasycode.currentItem().text())
        

        print ""
        print ""
        print ""
        print ""
        print ""
        print "requete dans double_clicked_multieasycode:"
        print req



        self.pg_select(query = req)
        print "printing row"
        print ""
        print ""
        print ""
        print ""

        # le double_t suivant est fait par expres
        listt__dl_fini_chemin_easycode = [] * (len(self.rows_pg))
        # listt__dl_fini_chemin_easycode = [[] for x in xrange(len(self.rows_pg))]
        
        
        for row in self.rows_pg:
            list01 = [None] * (len(row))
            for i in range(len(row)):
                if i == 0:
                    # download
                    # testena we 0 v ny row[i]
                    if row[i] == 0:
                        list01[i] = False
                    else:
                        list01[i] = True
                elif i == 1:
                    # fini
                    if row[i] == 0:
                        list01[i] = False
                    else:
                        list01[i] = True
                else:
                    list01[i] = row[i]
                
            print "qsdmlkfjqsmldfkjqsdlmfkj: "
            print list01
            listt__dl_fini_chemin_easycode.append(list01)
        # sys.exit(0)
            
        print ""
        print ""
        print ""
        print ""
        print ""
        print ""
        print "test000011"
        print listt__dl_fini_chemin_easycode
        # sys.exit(0)


        self.list__dl_fini_chemin_easycode = listt__dl_fini_chemin_easycode
        self.dialog_monoeasycode(
            list__dl_fini_chemin_easycode = listt__dl_fini_chemin_easycode
            )
        
        
        print ""
        print ""
        print ""
        print ""
        print ""
        print ""

        # dans double_clicked_multieasycode
        
        
        # fin double_clicked_multieasycode "TRAITES"





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
            table_campagne = "CT_NOMINATION_AS3",
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
            +table_campagne\
            +" INNER JOIN easy.dbo.data_context ON easy.dbo.data_context.contact = easy.dbo." \
            + table_campagne \
            + ".easycode " \
            +"INNER JOIN easy.dbo.thread ON easy.dbo.thread.data_context = easy.dbo.data_context.code " \
            +"INNER JOIN easy.dbo.call_thread " \
            +"ON easy.dbo.thread.code = easy.dbo.call_thread.code " \
            +"WHERE easy.dbo."\
            +table_campagne \
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
            root_local = "E:\\DISK_D\\ecoutes\\", 
            root_distant = "\\\\mcuci\\Storage$\\",
            telechargee = "0",
            fini = "0",
            monoeasy = "17868031"
        ):

        self.root_local = root_local
        self.root_distant = root_distant
        """
        ceci va retourner le Chemin du fichier.xlsx qu_on veut ajouter
        """
        
        # ndr1ndr1 refa atao indrepani ftsn ti d 
        self.remove_all_qtlist_multieasycode()
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
            # on a importer un fichier NON_xlsx
            return

        
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


        


        # mnw anle drop_table
        drop_query = "DROP TABLE IF EXISTS prj_ecoute01;"
        self.pg_not_select(drop_query)
        print "table: prj_ecoute01 est EFFACEE"



        # mnw anle creation_table
        create_query = "CREATE TABLE "\
            +"prj_ecoute01 " \
            +"(" \
            +"id_ecoute INTEGER NOT NULL DEFAULT NEXTVAL(('public.prj_ecoute01_seq'::text)::regclass)," \
            + "chemin__a_partir_root CHARACTER VARYING(254)," \
            + "root_local CHARACTER VARYING(128)," \
            + "root_distant CHARACTER VARYING(128)," \
            + "table_campagne CHARACTER VARYING(128)," \
            + "telechargee SMALLINT," \
            + "fini SMALLINT," \
            + "multi_easycode INTEGER," \
            + "mono_easycode INTEGER"  \
            +")"


        self.pg_not_select(create_query)
        print "table: prj_ecoute01 est CREEE"

        

        # mnw test we aiz no misi anlai fichier



        # manomboka eto dia : Formation de la requete_insert



        query_insert = "INSERT INTO " \
            + "prj_ecoute01 "\
            +"(chemin__a_partir_root, "\
            +"root_local, root_distant, "\
            +"telechargee, fini, "\
            +"multi_easycode, table_campagne) " +\
            "VALUES " 
            

        #dans import_xls
        sheet0 = book.sheet_by_index(0)
        list_multieasycode = []

        # alaina ts1r1 ny multi_easycode izai ani am fichier.xlsx
        # ni multi_easycode=multieasyc_i dia mety manana enregistrement maro2
        for i in range(0, sheet0.nrows):
            # multieasyc_i dia meti manana enregistrement maro2
            multieasyc_i = sheet0.row_values(i, 0, 1)[0]

            # sys.exit(0)
            cheminS = self.select_chemin(
                table_campagne = self.combo_box__campagne.currentText(),
                multieasy = str(multieasyc_i)[:-2]
            );
            # pour verifier que multieasyc_i est present
                # if (
                        # self.check_existance_pg_int (
                            # table01 = "prj_ecoute01",
                            # chp01 = "multi_easycode",
                            # val = multieasyc_i
                        # ) == False
                    # ):
                    # print "Tsy ao: " + str(multieasyc_i)
                # else:
                    # print "AO tsara: " + str(multieasyc_i)

            # multieasyc_i dia meti manana enregistrement maro2
            # # ireto manaraka ireto ni chemin maka ani am enregistrement an_i easycode irai
            

            # sarotsarotra azavaina ti aah!
            # hafa ni requete rah ohatra ka ani am farani n easycode ani am 
            # # fichier.xlsx no jerena ni enregistrement
            if i != (sheet0.nrows-1):
                cpt_chm = 0
                for chemin in cheminS:
                    test_exist_fichier = self.root_distant + chemin

                    samba_ = "\\\\192.168.10.19\\voice\\"
                    file01 = Path(samba_ + chemin)
                    if (
                            # ao am Voice
                            file01.is_file()
                        ):
                        root_distant = "\\\\192.168.10.19\\voice\\"
                        print root_distant + chemin
                        # sys.exit(0)
                    # elif (
                            # # self.samba_check_file(
                                # # remote_file = chemin 
                            # # ) == "\\\\192.168.10.19\\voice\\"
                        # ):
                        # root_distant = "\\\\192.168.10.19\\voice\\"
                    else: # itest ao am Storage
                        samba_ = "\\\\mcuci\\Storage$\\"
                        file01 = Path(samba_ + chemin)
                        if (
                            # ao am Voice
                            file01.is_file()
                        ):
                            root_distant = "\\\\mcuci\\Storage$\\"

                    # sys.exit(0)
                    if cpt_chm != (len(cheminS) - 1):
                        query_insert += "( '"
                        query_insert += chemin + "', '" \
                        + root_local + "', '"\
                        + root_distant + "', '"\
                        + telechargee + "', '"\
                        + fini + "', "\
                        + str(int(multieasyc_i)) + ", '" \
                        + self.combo_box__campagne.currentText()\
                        + "'), "
                    else:
                        query_insert += "( '"
                        query_insert += chemin + "', '" \
                        + root_local + "', '"\
                        + root_distant + "', '"\
                        + telechargee + "', '"\
                        + fini + "', "\
                        + str(int(multieasyc_i)) + ", '"\
                        + self.combo_box__campagne.currentText()\
                        + "'), "
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
                        + str(int(multieasyc_i)) + ", '"\
                        + self.combo_box__campagne.currentText()\
                        + "'), "
                    else:
                        query_insert += "( '"
                        query_insert += chemin + "', '" \
                        + root_local + "', '"\
                        + root_distant + "', '"\
                        + telechargee + "', '"\
                        + fini + "', "\
                        + str(int(multieasyc_i)) + ", '"\
                        + self.combo_box__campagne.currentText()\
                        + "') "
                    cpt_chm = cpt_chm + 1

                print ""
                print ""
                print ""
                print ""
                print ""
                print "query_insert dans import_xls __code__005874: " + query_insert

                list_multieasycode.append(
                    multieasyc_i
                    )


        print "query_insert dans import_xls __code002__: " + query_insert



        # ty tsy olana fa ilai fanamboarana anlai requete no enjana
        self.cursor_pg.execute(query_insert)

        # eto ni mnw insertion
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



        #fin_import_xls


    def check_existance_pg_int(self,
        bool01 = True, 
            table01 = "prj_ecoute01", 
            chp01 = "chemin__a_partir_root",
            val = '2017\\06\\23\\12\\05\\460003e0aa8c000001540594d04022591000f86e60001000003.wav'
        ):
        req = "SELECT EXISTS" \
            + "(SELECT * FROM " \
            + table01 \
            + " WHERE " \
            + chp01 \
            + " = "\
            + str(val) \
            + ");"
        res = True
        self.cursor_pg.execute(req)
        rows = self.cursor_pg.fetchall()
        # print rows
        if len(rows) != 0:
            res = True
        else:
            res = False

        print "resultat0564614: " + str(res)
        return res

    def clicked_bouton_fermer_dialog(self):
        self.dialog01.close()
        print "this is from the dialog"

    def check_existance_pg_str(self, 
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
            + str(val) \
            + "');"
        res = True
        self.cursor_pg.execute(req)
        rows = self.cursor_pg.fetchall()
        # print rows
        if len(rows) != 0:
            res = True
        else:
            res = False

        print "resultat0564614: " + str(res)
        return res




    def pg_not_select(self, query):
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
        # for a in list_call_date01 :
            # if (str(a)[-2:] == ".0"):
                # self.qtlist_multieasycode.\
                    # addItem(str(a)[:-2])
            # else:
                # self.qtlist_multieasycode.\
                    # addItem(str(a))




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
            samba_server = "\\\\mcuci\\Storage$\\",
            # samba_server = "\\\\192.168.10.19\\voice\\",
            remote_file = "2017\\07\\05\\14\\03\\050003e0aa8c000001540595cf1976568001369720001000149.wav"):
        
        path_to_file = samba_server + remote_file

        # testena ao am storage
        my_file = Path(path_to_file)
        if my_file.is_file():
            print "ato am storage"
            print path_to_file
            # sys.exit(0)
            return samba_server
        else:
            samba_server_voice = "\\\\mcuci\\Storage$\\"
            path_to_file = samba_server_voice + remote_file
            my_file = Path(path_to_file)
            if my_file.is_file():
                print "ao am voice"
                return samba_server_voice
            else:
                print "fichier inexistant: " + remote_file
                return "inexistant"


        # return my_file.is_file()

        # os.system()


        # print ""


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
            # sys.exit(0)
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
            # self.check_existance_pg_int
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
                [False, True, 'chemin01', 'easycode04'],
                [True, False, 'chemin02', 'easycode02'],
                [True, False, 'chemin03', 'easycode03'],
                [False, True, 'chemin04', 'easycode01'],
                [True, True, 'chemin05', 'easycode05'],
            ]
        ):

        # misi requete insertion

        # misi requete update

        # #instanciation inside dialog
        self.dialog01 = QtGui.QDialog()
        qvbox_layout_dialog = QtGui.QHBoxLayout(self.dialog01)
        
        self.button01 = QtGui.QPushButton("ok", self.dialog01)
        self.button01.clicked.connect(self.clicked_bouton_fermer_dialog)


        rows = len(list__dl_fini_chemin_easycode)
        cols = len(list__dl_fini_chemin_easycode[0])
        self.qtable01 = QtGui.QTableWidget(rows, cols, self.dialog01)
        self.qtable01.setSelectionBehavior(QtGui.QTableView.SelectRows)


        self.dialog01.setMinimumSize(600, 50)
        self.qtable01.setStyleSheet(
            '''
            QTableWidget { max-width: 600px; min-height: 200px;}
            '''
            )
        qvbox_layout_dialog.addWidget(self.button01)
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
                    item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    self.qtable01.setItem(row, col, item)
                elif col == 3:
                    # easycode
                    item = QtGui.QTableWidgetItem(
                        str(list__dl_fini_chemin_easycode[row][col])
                    )
                    item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    self.qtable01.setItem(row, col, item)


        self.dialog01.setWindowTitle("Dialog")
        self.dialog01.setWindowModality(QtCore.Qt.ApplicationModal)
        self.dialog01.exec_()

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