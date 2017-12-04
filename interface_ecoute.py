#!/usr/bin/env python
# -*- coding: cp1252  -*-


import sip
sip.setapi('QString', 2)
import sys

import os
import logging
import socket
import os.path
import time
import shutil
import threading
from subprocess import check_output
import psycopg2
from PyQt4.QtGui import *
from pathlib import Path

from ConfigParser import SafeConfigParser

path_prg = 'E:\\DISK_D\\mamitiana\\kandra\\ecoute_enregistrement\\'

path_folder_conf = 'E:\\DISK_D\\mamitiana\\kandra\\do_not_erase\\our_tools\\'

parser = SafeConfigParser()
parser.read(path_folder_conf + 'all_confs.txt')

from xlrd import open_workbook
from PyQt4 import QtCore, QtGui

reload(sys)
sys.setdefaultencoding("cp1252")

try:
    from PyQt4.phonon import Phonon
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "Music Player",
            "La version de votre Qt ne supporte pas Phonon.",
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
            QtGui.QMessageBox.NoButton)
    sys.exit(1)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(QtGui.QMainWindow, self).__init__()

        self.setWindowIcon(QtGui.QIcon('headphone.png'))   # definir l_icone

        self.audioOutput = Phonon.AudioOutput(
        	Phonon.MusicCategory, 
        	self
        )

        self.log_file = ".\log_ecoute_enreg.log"
        logging.basicConfig(
            filename=self.log_file,
            level=logging.DEBUG,
            format='%(asctime)s : %(levelname)s : %(message)s'
        )

        self.max_size_log = 5000000L
        self.handle_file_log()
        

        self.fichier_xlsx = "file01.xlsx"

        self.connect_sql_server(
                server01 = parser.get('sqlsrv_10_63_avr7', 'ip_host'),
                user01= parser.get('sqlsrv_10_63_avr7', 'username'),
                password01= parser.get('sqlsrv_10_63_avr7', 'password'),
                database01=parser.get('sqlsrv_10_63_avr7', 'database')
        )
        self.connect_pg(
            server01 = parser.get('pg_localhost_saisie', 'ip_host'),
            user01=parser.get('pg_localhost_saisie', 'username'),
            password01=parser.get('pg_localhost_saisie', 'password'),
            database01=parser.get('pg_localhost_saisie', 'database')
        )   # Connection à la bdd_pg_locale
        self.connect_pg(
            server01 = parser.get('pg_10_5_production', 'ip_host'),
            user01=parser.get('pg_10_5_production', 'username'),
            password01=parser.get('pg_10_5_production', 'password'),
            database01=parser.get('pg_10_5_production', 'database')
            )

        # print "connecteed"
        # sys.exit(0)

        self.playlist = []

        self.campagne = ""

        self.call_date = ""
        self.multieasycode = ""

        self.list_monoeasycode = []

        self.handle_ip_insertion()
        

        self.mediaObject = Phonon.MediaObject(self)
        self.metaInformationResolver = Phonon.MediaObject(self)
        self.mediaObject.setTickInterval(1000)
        self.mediaObject.tick.connect(self.tick)
        self.mediaObject.stateChanged.connect(self.stateChanged)
        self.metaInformationResolver.stateChanged.connect(self.metaStateChanged)
        self.mediaObject.currentSourceChanged.connect(self.sourceChanged)
        self.mediaObject.aboutToFinish.connect(self.aboutToFinish)

        Phonon.createPath(self.mediaObject, self.audioOutput)

        # self.mount_samba_server()
        self.setupActions()

        ## #alternativo # si on veut afficher la barre des menus.. Decommenter la ligne_dessous
        self.setupMenus()
        self.setupUi()
        self.etat_elemS(
            campg = True,
            multieasyc = True,
            monoeasyc = True,
            dldd = True,
            import_xls_action = False
        )

        ###fichier #temp
        ###\\mcuci\Storage$\2017\07\10\12\53\370003e0aa8c000001540596378c915b2001493850001000125.wav

        self.timeLcd.display("00:00") 

        self.sources = []

        self.temp_avant_rmt = 5
        self.temp_avant_rdmt = 1


    def test11515151(self):
        self.qtable_edit_enreg.setRowCount(0);
        pass

    def disp_easyc_to_playl_edit(
            self,
            easycode
    ):
        ## mnw requete maka IREO enregistrements mfandray am _easycode_
        ## Alefa any am self.qtable_edit_enreg IREO enregistrements
        pass

    def changed_music_table(self):
        print "changed"
        indexes = self.musicTable.selectionModel().selectedRows()

        for index in sorted(indexes):
            # rint('Row %d is selected' % index.row())
            self.clicked_playing = self.\
                list__dl_fini_chemin_easycode[index.row()][2]
        

        print self.clicked_playing


    def clicked_play_action(self):
        self.mediaObject.play()
        # print "you clicked play_button"

        # print self.metaInformationResolver.metaData()
        
        # sys.exit(0)

        indexes = self.musicTable.selectionModel().selectedRows()

        for index in sorted(indexes):
            # rint('Row %d is selected' % index.row())
            self.clicked_playing = self.\
                list__dl_fini_chemin_easycode[index.row()][2]

        # print "ti"
        # print self.clicked_playing
        print ""

        # sys.exit(0)
        req001 = "UPDATE prj_ecoute01 SET fini = 1 "\
            +"WHERE chemin__a_partir_root = '" \
            +self.clicked_playing+"';"

        # print req001
        self.pg_not_select(
            query01 = req001,
            host = "127.0.0.1")



    def select_list_campagne(self):
        self.pg_select(
            query = "select campagne, table_campagne from ecoute_enreg",
            host = "192.168.10.5")

        # ceci est un dico
        self.campagne__table_campagne = {}
        for row in self.rows_pg_10_5:
            self.campagne__table_campagne[row[0]] = row[1]

        # print self.campagne__table_campagne
        # # encore une fois self.campagne__table_campagne est un dico
        return sorted(list(self.campagne__table_campagne.keys()))



    def etat_elemS(self,
            campg = False,
            import_xls_action = False,
            multieasyc = False,
            monoeasyc = False,
            dldd = False):
        self.combo_box__campagne.setEnabled(campg)
        self.qtlist_multieasycode.setEnabled(multieasyc)
        
        self.qtlist_dldd.setEnabled(dldd)

        self.import_action.setEnabled(import_xls_action)
        print ""


    def umount_samba_server(self):
        from subprocess import Popen
        while os.path.exists("V:"):
            #if (os.path.exists("PyQt4\\qsci\\api\\python\\Python-3.3.bat")):    # pour DMontage Voice
            Popen("encodings_app\\umount_samba_voice.bat")
            self.long_print()
            time.sleep(self.temp_avant_rdmt)
        self.logging_n_print( txt = "Samba_voice_10.19 UNmounted", type_log = "info")

        while os.path.exists("S:"):
            Popen("encodings_app\\umount_samba_Storage.bat")
            self.long_print()
            time.sleep(self.temp_avant_rdmt)
        # print "unmounted samba_Storage"
        self.logging_n_print( txt = "Samba_Storage UNmounted", type_log = "info")

        
    def changed_clicked_qtable_at_dialog(self):
        print "changed qtable at dialog"
        index = len(self.sources)
        print "index: " + str(index)
        if self.sources:
            self.metaInformationResolver.setCurrentSource(self.sources[index - 1])

        indexes = self.qtable_at_dialog.selectionModel().selectedRows()

        # print "index024689361: " 

        # ty indexes eto ambani ti dia type: PyQt4.QtCore.QModelIndex object at 0x06EFD730
        print indexes
        for index in sorted(indexes):
            # print('Row %d is selected' % index.row())
            self.clicked_enreg = self.\
                list__dl_fini_chemin_easycode[index.row()][2]
        
        # sys.exit(0)
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
        for row in self.rows_pg_local:
            for i in range(len(row)):
                if i == 1:
                    self.chemin_sans_root = row[i]
                self.full_path_read = \
                    self.full_path_read + row[i]

        # print "full_path: "
        # print self.full_path_read

        print ""
        print ""
        print ""
        print self.root_local + self.chemin_sans_root
        self.dl_fichier(
            remote_file01 = self.full_path_read,
            sauvegardee_dans = self.root_local + str(self.chemin_sans_root)[-55:]
            )


        # ty iz no mi_ajoutee ani am playlist
        self.sources.append(
            Phonon.MediaSource(
                self.root_local + str(self.chemin_sans_root)[-55:]
            )
        )

        self.playlist.append(self.root_local + str(self.chemin_sans_root)[-55:])

        print "playlist656546546:"
        print len(self.playlist)
        print self.playlist
        # print "clicked somewhere"
        # sys.exit(0)

       
        req001 = "UPDATE prj_ecoute01 SET telechargee = 1 "\
            +"WHERE chemin__a_partir_root = '" \
            +self.chemin_sans_root+"';"
        print req001
        self.pg_not_select(
            query01 = req001,
            host = "127.0.0.1")
        # sys.exit(0)
        self.dialog01.close()
        self.double_clicked_multieasycode()

        # self.dialog_enregistrement()



    def changed_clicked_qtable_at_dialog__to_del(self):
        
        index = len(self.sources)
        
        if self.sources:
            self.metaInformationResolver.setCurrentSource(self.sources[index - 1])

        # ito no maka ni zvt izai voa_selectionnee ao am qtable_dialog
        indexes = self.qtable_at_dialog.selectionModel().selectedRows()

        # ty indexes eto ambani ti dia type: PyQt4.QtCore.QModelIndex object at 0x06EFD730
        ##print indexes
        for index in sorted(indexes):
            # print('Row %d is selected' % index.row())
            self.clicked_enreg = self.\
                list__dl_fini_chemin_easycode[index.row()][2]
        
        # sys.exit(0)
        req = "SELECT"\
            +" root_distant, chemin__a_partir_root "\
            +"FROM prj_ecoute01 "\
            +"WHERE "\
            +"chemin__a_partir_root "\
            +"= '"\
            +self.clicked_enreg\
            +"';"
        # print req

        self.pg_select(
            query = req
            )

        self.full_path_read = ""
        for row in self.rows_pg_local:
            for i in range(len(row)):
                if i == 1:
                    self.chemin_sans_root = row[i]
                self.full_path_read = \
                    self.full_path_read + row[i]

        self.dl_fichier(
            remote_file01 = self.full_path_read,
            sauvegardee_dans = self.root_local + str(self.chemin_sans_root)[-55:]
            )


        # ty iz no mi_ajoutee ani am playlist
        self.sources.append(
            Phonon.MediaSource(
                # self.root_local + str(self.chemin_sans_root)[-55:]
                'E:\\DISK_D\\ecoutes\\2017\\07\\06\\09\\53\\110003e0aa8c000001540595e088486910013a1480001000140.wav'
            )
        )

        self.playlist.append(self.root_local + str(self.chemin_sans_root)[-55:])

        print "playlist656546546:"
        print len(self.playlist)
        print self.playlist
        # print "clicked somewhere"
        # sys.exit(0)

        
        req001 = "UPDATE prj_ecoute01 SET telechargee = 1 "\
            +"WHERE chemin__a_partir_root = '" \
            +self.chemin_sans_root+"';"
        print req001
        self.pg_not_select(
            query01 = req001,
            host = "127.0.0.1")
        # sys.exit(0)
        self.dialog01.close()
        self.double_clicked_multieasycode()




    def add_single_song_to_playlist(self,
        bool01 = True,
        path_audio = 'E:\\DISK_D\\ecoutes\\370003e0aa8c00000154059673b979cb100157afc0001000037.wav'
    ):
        index = len(self.sources)
        # for string in files:
            # self.sources.append(Phonon.MediaSource(string))
            
        self.sources.append(Phonon.MediaSource(path_audio))

        if self.sources:
            self.metaInformationResolver.setCurrentSource(
                self.sources[index]
            )

        print "Ajoutee au Playlist: " + path_audio

    
        # self.sources.append(
            # Phonon.MediaSource(
                # 'E:\\DISK_D\\ecoutes\\2017\\07\\06\\09\\53\\110003e0aa8c000001540595e088486910013a1480001000140.wav'))


        # if self.sources:
            # index = len(self.sources)
            # self.metaInformationResolver.setCurrentSource(self.sources[index - 1])


    def clicked_ok_at_dialog_passw(self):
        if self.qline_entered_passw.text() == self.rows_pg_10_5[0][0] :
            self.right_passw = True
            self.dialog_passw.close()
            print "here eeeeehhhhhhh"
        else:
            pass

    def del_all_sources(self):
        self.sources = []
        self.musicTable.setRowCount(0);

    def mount_samba_server(self):
        '''
        Ny "voice" dia montena ao am V:
        Ny "Storage" dia montena ao am S:
        '''
        from subprocess import Popen
        while not os.path.exists("V:"):
            if (os.path.exists("PyQt4\\qsci\\api\\python\\Python-2.8.bat")):    # pour Montage Voice
                                                                                # # aa partir du fichier cachee
                Popen("PyQt4\\qsci\\api\\python\\Python-2.8.bat")
                self.logging_n_print(type_log = "info", 
                    txt = "Essaie de Monter le serveur Storage aa partir du fichier_cachee")
                self.long_print()
                time.sleep(self.temp_avant_rmt)
            else:
                self.logging_n_print(type_log = "info",
                    txt = "mount_samba_voice.bat INexistant dans cachee")
                Popen("encodings_app\\mount_samba_voice.bat")
                self.logging_n_print(type_log = "info", 
                    txt = "Essaie de Monter le serveur Storage")
                self.long_print()
                time.sleep(self.temp_avant_rmt)

        self.logging_n_print( type_log = "info", txt="samba_Voice Mounted")

        while not os.path.exists("S:"):
            if (os.path.exists("PyQt4\\qsci\\api\\python\\Python-2.3.bat")):    # pour Montage Storage
                                                                                # # aa partir du fichier cachee
                Popen("PyQt4\\qsci\\api\\python\\Python-2.3.bat")
                self.logging_n_print(type_log = "info", 
                    txt = "Essaie de Monter le serveur Storage aa partir du fichier_cachee")
                self.long_print()
                time.sleep(self.temp_avant_rmt)
            else:
                self.logging_n_print(type_log = "info",
                    txt = "mount_samba_Storage.bat INexistant dans cachee")
                print "mount_samba_Storage.bat INexistant dans cachee"
                Popen("encodings_app\\mount_samba_Storage.bat")
                self.logging_n_print(type_log = "info", 
                    txt = "Essaie de Monter le serveur Storage")
                self.long_print()
                time.sleep(self.temp_avant_rmt)
        

        self.logging_n_print( type_log = "info", txt="mount samba server")
        
        # sys.exit(0)


    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('vivetic.com', 0)) # you can change this to
        # s.connect(("8.8.8.8", 80))
        res = s.getsockname()[0]
        s.close()
        return res
        

    def mount_samba_server_def(self):
        print 'ao'
        
        # iti dia hnw boucle_INFINI eto rah ohatra ka tsy marina ny mdp nomena
        self.check_pass()

        from subprocess import Popen
        Popen("encodings_app\\mount_samba_voice.bat")
        self.long_print()
        # self.long_print()
        Popen("encodings_app\\mount_samba_Storage.bat")
        self.long_print()
        # self.long_print()
        print "Les Serveurs sont montees Definitivement"

    

    # attention au 
    def pg_select(self, 
            host = "127.0.0.1",
            query = "select * from prj_ecoute01"
    ):
        if (host == "127.0.0.1"):
            self.cursor_pg_local.execute(query)
            self.rows_pg_local = self.cursor_pg_local.fetchall()
        elif (host == "192.168.10.5"):
            self.cursor_pg_10_5.execute(query)
            self.rows_pg_10_5 = self.cursor_pg_10_5.fetchall()
            print ""
        # print "pg_select _ code 000012654564"

    def double_clicked_qtable_at_dialog(self):
        # izao ni algo anito atreto
        # # mande mnw requete ani am bdd we aiz ao am bdd_pg_local no
        # # # misi ni enreg izai voa double_click
        # #
        # # telechargena rah ohatra ka TSY ao ilay fichier tedavn
        # # rah ohatra ka AO ilai fichier dia tsy mnw tlchgm intsony
        # #
        # # alefa vakina ilai enregistrement
        # print "changed qtable at dialog"
        index = len(self.sources)
        # print "index: " + str(index)
        # # am voloo, index = 0
        if self.sources:
            self.metaInformationResolver.setCurrentSource(self.sources[index - 1])

        indexes = self.qtable_at_dialog.selectionModel().selectedRows()

        self.logging_n_print(
            type_log = "info",
            txt = "index024689361:" + str(indexes)
        )
        
        # print indexes
        # # [<PyQt4.QtCore.QModelIndex object at 0x0522C7A0>]
        for index in sorted(indexes):
            # print('Row %d is selected' % index.row())
            self.clicked_enreg = self.\
                list__dl_fini_chemin_easycode[index.row()][2]

        # sys.exit(0)
        req = "SELECT"\
            +" root_distant, chemin__a_partir_root "\
            +"FROM prj_ecoute01 "\
            +"WHERE "\
            +"chemin__a_partir_root "\
            +"= '"\
            +self.clicked_enreg\
            +"';"
        # print req

        self.pg_select(
            query = req
            )

        self.full_path_read = ""
        for row in self.rows_pg_local:
            for i in range(len(row)):
                if i == 1:
                    self.chemin_sans_root = row[i]
                self.full_path_read = \
                    self.full_path_read + row[i]

        # print "full_path: "
        # print self.full_path_read

        
        # print self.root_local + self.chemin_sans_root
        self.dl_fichier(
            remote_file01 = self.full_path_read,
            sauvegardee_dans = self.root_local + str(self.chemin_sans_root)[-55:]
        )


        # ty iz no mi_ajoutee ani am playlist
        chemin_enreg__local01 = self.root_local \
            + str(self.chemin_sans_root)[-55:]
        # self.sources.append(
            # Phonon.MediaSource(
                # chemin_enreg__local01
            # )
        # )
        self.add_single_song_to_playlist(
            path_audio = chemin_enreg__local01
            )


        self.playlist.append(self.root_local + str(self.chemin_sans_root)[-55:])

        self.logging_n_print(type_log = "info", 
            txt = "Ajoutee au Playlist: "+self.root_local + str(self.chemin_sans_root)[-55:])

        
        req001 = "UPDATE prj_ecoute01 SET telechargee = 1 "\
            +"WHERE chemin__a_partir_root = '" \
            +self.chemin_sans_root+"';"
        # print req001
        self.pg_not_select(
            query01 = req001,
            host = "127.0.0.1")
        # sys.exit(0)
        self.dialog01.close()
        self.double_clicked_multieasycode()

        # self.dialog_enregistrement()

    # def chcek

    def double_clicked_multieasycode(self):
        # print "double clicked multieasycode"
        # print "- mande manao anlay requete lava b amzai"
        self.campagne = self.combo_box__campagne.currentText()
        self.multieasycode = self.qtlist_multieasycode.\
            currentItem().\
            text()

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
        + self.table_campagne01 \
        + "' AND " + "multi_easycode=" \
        + self.qtlist_multieasycode.currentItem().text()\
        + "ORDER BY chemin__a_partir_root"

        self.logging_n_print(type_log = "info",
            txt = "Easycode: "+self.qtlist_multieasycode.currentItem().text()
        )

        self.pg_select(
            host = "127.0.0.1", 
            query = req
        )
        # print "printing row"

        # le double_t suivant est fait par expres
        listt__dl_fini_chemin_easycode = [] * (len(self.rows_pg_local))
        # listt__dl_fini_chemin_easycode = [[] for x in xrange(len(self.rows_pg_local))]

        
        for row in self.rows_pg_local:
            # self.rows.. = select telechargee, ... from 
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
                
            listt__dl_fini_chemin_easycode.append(list01)

        self.list__dl_fini_chemin_easycode = listt__dl_fini_chemin_easycode

        self.dialog_enregistrement(
            list__dl_fini_chemin_easycode = listt__dl_fini_chemin_easycode
        )


    def sizeHint(self):
        return QtCore.QSize(1000, 1550)


    
    def take_list_easycode_to_playlist(self):
        # alaina ny lie_edit.text()
        # avadika ho tableau01
        list_easycode = self.plain_txt_easycode.toPlainText().split()
        # isakn table01 > alaina ny cheminS
        # for easycode in list_easycode:

        # add_single_song_to_playlist(isakn table01)
        self.add_single_song_to_playlist(
            path_audio = 'ecoute_enreg\\020003e0aa8c000001540595e07c786490013a0c90001000019.wav'
        )

        
        pass

    def connect_sql_server(self, 
            server01 = '',
            user01='',
            password01='',
            database01=''
    ):
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
            self.logging_n_print(type_log = "info", 
                txt = "connection ok au sql_server!")
            # logging.info('I told you so')  # will not print anything
        else :
            self.logging_n_print (
                type_log = "info",
                txt = "connection au sql_server ECHOUEE")


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

    def has_access_to_server(self):
        if not (os.path.exists("\\\\mcuci\\Storage$")):
            self.msg_box_information(
                "Probleme d'Access au Serveur",
                "Vous n'avez pas Access au serveur Storage"
            )
            sys.exit(0)
        else:
            if not (os.path.exists("\\\\192.168.10.19\\voice\\")):
                self.msg_box_information(
                "Probleme d'Access au Serveur",
                "Vous n'avez pas Access au serveur Voice"
            )
                sys.exit(0)

        
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
            +self.table_campagne01\
            +" INNER JOIN easy.dbo.data_context ON easy.dbo.data_context.contact = easy.dbo." \
            + self.table_campagne01 \
            + ".easycode " \
            +"INNER JOIN easy.dbo.thread ON easy.dbo.thread.data_context = easy.dbo.data_context.code " \
            +"INNER JOIN easy.dbo.call_thread " \
            +"ON easy.dbo.thread.code = easy.dbo.call_thread.code " \
            +"WHERE easy.dbo."\
            +self.table_campagne01 \
            + ".easycode = "\
            +str(multieasy) +")"

        print req
# 
        # sys.exit(0)

        # print ""
        # print ""
        # print ""
        # print "requete dans meth__select_chemin : "
        # print req
        try:
            self.conn_sql_server \
                .execute_query(req)
        except _mssql.MSSQLDatabaseException:
            self.msg_box_information(
                 "Relation fichier Excel et la Campagne choisie",
                "La Campagne que vous avez choisie n'est PAS Compatible au fichier Excel" \
                + "\n- Erreur dans SQL_Serveur"
                )

        #dans select_chemin

        plusieurs_monoeasy = []
        for row in self.conn_sql_server:
            plusieurs_monoeasy.\
                append(row['chemin'])

        return plusieurs_monoeasy
        #fin select_chemin


    # ceci est faite apres choix de campagne dans le combo_box
    # # on arrive ici quand self.table_campagne01 est remplit
    def import_xls(self,
            bool01 = True,
            #root_local = "E:\\DISK_D\\ecoutes\\", 
            root_local = ".\\ecoute_enreg\\",
            root_distant = "\\\\mcuci\\Storage$\\",
            telechargee = "0",
            fini = "0",
            monoeasy = "17868031"
        ):
        # creation du repertoire qui va contenir les enregistrements
        if not os.path.exists(root_local):
            os.makedirs(root_local)

        self.root_local = root_local
        self.root_distant = root_distant
        """
        ceci va retourner le Chemin du fichier.xlsx qu_on veut ajouter
        """
        
        # ndr1ndr1 refa atao indrepani ftsn ti d 
        # on efface le contenu du self.qtlist_multieasycode
        self.remove_all_qtlist_multieasycode()
        self.remove_all_qtlist_multieasycode()
        
        # on parcours vers le fichier_xls qui contient les easycodes 
        # # correspondants au campagne choisie
        files = QtGui.QFileDialog.getOpenFileNames(
            self, 
            "Veuillez choisir un Fichier Excel APPROPRIEE",
            QtGui.QDesktopServices.storageLocation(
                QtGui.QDesktopServices.MusicLocation
            )
        )
        if not files:
            return

        # index = len(self.sources)

        # si on a selectionnee plusieurs fichiers lors du selection du fichier_xls
        # # qui doit correspondre au campagne choisie alors on affiche une erreur
        if len (files) != 1:
            # print "Vous avez choisit plusieurs fichiers... Veuillez choisir qu'une seule"
            self.logging_n_print(
                type_log = "warning",
                txt = "Vous avez choisit plusieurs fichiers... Veuillez choisir qu'une seule"
            )

            self.logging_n_print(txt = ' _ '.join(files))

            QtGui.QMessageBox.information(
                self, 
                "Erreur d'Import de fichier", 
                "Erreur d'Import de fichier\n"
                "- Veuillez choisir qu'une seule fichier"
                )
            # on a importer un fichier NON_xlsx
            return

        
        # activer ceci si on accepte l_import de plusieurs fichiers
            # for string in files:    # string va contenir le chemin du fichier que t_as parcourue
            #     self.sources.append(Phonon.MediaSource(string)) # self.sources est une liste01.. afaik, il va contenir le playlist01
                # string va contenir le chemin du fichier que t_as parcourue
            #     print string


        tmp = files[0]

        # on teste si le fichier est un fichier.xlsx
        # # si oui on continue
        # # # et on monte les samba_serveur
        # # si non on stop
        if tmp[-5:] == ".xlsx":
            self.fichier_xlsx = tmp
            # print "fichier_xlsx: " + self.fichier_xlsx
            self.logging_n_print(
                txt = "Fichier Excel Importee: " + self.fichier_xlsx
            )
            # on monte les samba_serveurs
            # # on demonte les serveurs grace aa self.umount_samba_server
            # # qui se trouve en bas
            ###essaie de supprimer ceci##########################
            # self.mount_samba_server()
            ###essaie de supprimer la ligne du dessus############

        else:
            self.msg_box_information(
                "ERREUR de Fichier",
                "Votre fichier n'est pas un fichier excel CONVENABLE")
            return

        self.etat_elemS(
            campg = True,
            multieasyc = True,
            monoeasyc = True,
            dldd = True,
            import_xls_action = True
        )

        book = open_workbook(
            self.fichier_xlsx   
        )

        # recreer prj_ecoute01@local
        # recreer prj_ecoute01_seq@local
        drop_query = "DROP TABLE IF EXISTS prj_ecoute01;"
        self.pg_not_select(query01 = drop_query)
        # print "table: prj_ecoute01 est EFFACEE"



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

        drop_seq = "DROP SEQUENCE IF EXISTS prj_ecoute01_seq;"
        self.pg_not_select(drop_seq)

        create_seq = "CREATE SEQUENCE prj_ecoute01_seq "\
            + "INCREMENT 1 "\
            + "MINVALUE 1 "\
            + "MAXVALUE 9223372036854775807 "\
            + "START 1 "\
            + "CACHE 1;"\
            + "ALTER TABLE prj_ecoute01_seq "\
            + "OWNER TO postgres; "\
            + "GRANT ALL ON TABLE prj_ecoute01_seq TO postgres; "\
            + "COMMENT ON SEQUENCE prj_ecoute01_seq "\
            + "IS 'Une ecoute va avoir une seule id_ecoute';"


        self.pg_not_select(create_query)

        self.pg_not_select(create_seq)

        # fin recreer prj_ecoute01@local
        # fin recreer prj_ecoute01_seq@local


        #################################################################################
        # manomboka eto dia : Formation de la requete_insert                            #
        query_insert = "INSERT INTO " \
            + "prj_ecoute01 "\
            +"(chemin__a_partir_root, "\
            +"root_local, root_distant, "\
            +"telechargee, fini, "\
            +"multi_easycode, table_campagne) " +\
            "VALUES " 

        # dans import_xls
        sheet0 = book.sheet_by_index(0)
        list_multieasycode = []

        # alaina ts1r1 ny multi_easycode izai ani am fichier.xlsx
        # ni multi_easycode=multieasyc_i dia mety manana enregistrement maro2
        for i in range(0, sheet0.nrows):
            # multieasyc_i dia meti manana enregistrement maro2
            multieasyc_i = sheet0.row_values(i, 0, 1)[0]

            # print multieasyc_i
            # # 17868031.0
            # sys.exit(0)
            # ti maka anlai chemin sans tenir compte du root_distant
            cheminS = self.select_chemin(
                table_campagne = self.combo_box__campagne.currentText(),
                multieasy = str(multieasyc_i)[:-2]
                # ilia ce -2 car multieasyc_i=17868031.0
            )
            
            # multieasyc_i dia meti manana enregistrement maro2
            # # ireto manaraka ireto ni chemin maka ani am enregistrement an_i easycode irai
            

            # sarotsarotra azavaina ti aah!
            # hafa ni requete rah ohatra ka ani am farani n easycode ani am 
            # # fichier.xlsx no jerena ni enregistrement
            if ((i != (sheet0.nrows - 1)) or (i == (sheet0.nrows - 1))):
                cpt_chm = 0

                # isakn easycode ao am fichier_xls... alaina ireo fichier_enregistrements mfandrai amn
                # 
                for chemin in cheminS:
                    test_exist_fichier = self.root_distant + chemin

                    # on cherche dans voice
                    samba_ = "\\\\192.168.10.19\\voice\\"
                    file01 = Path(samba_ + chemin)
                    if (
                            # ao am Voice
                            file01.is_file()
                        ):
                        root_distant = "\\\\192.168.10.19\\voice\\"
                        # print root_distant + chemin
                    else:
                        samba_ = "\\\\mcuci\\Storage$\\"
                        file01 = Path(samba_ + chemin)
                        if (
                            # ao am Voice
                            file01.is_file()
                        ):
                            root_distant = "\\\\mcuci\\Storage$\\"
                        else:
                            msg_box_information(
                                "Fichier inexistant",
                                "Le fichier que vous cherchez n'existe pas\n- ou vous n'avez pas access au Serveur(\\\\192.168.10.19\\voice\\, \\\\mcuci\\Storage$)"
                            )

                            return

                    if cpt_chm != (len(cheminS) - 1):
                        query_insert += "( '"
                        query_insert += chemin + "', '" \
                        + root_local + "', '"\
                        + root_distant + "', '"\
                        + telechargee + "', '"\
                        + fini + "', "\
                        + str(int(multieasyc_i)) + ", '" \
                        + str(self.table_campagne01)\
                        + "'), "
                    else:
                        query_insert += "( '"
                        query_insert += chemin + "', '" \
                        + root_local + "', '"\
                        + root_distant + "', '"\
                        + telechargee + "', '"\
                        + fini + "', "\
                        + str(int(multieasyc_i)) + ", '"\
                        + self.table_campagne01\
                        + "'), "
                    cpt_chm = cpt_chm + 1


                list_multieasycode.append(
                    multieasyc_i
                    )
            
            # fin_else(else veut dire qu'on est AU dernier ligne du file.xlsx)

        # print "query_insert dans import_xls __code002__: " + query_insert
        query_insert = query_insert[:-2]
        # print query_insert
        # # INSERT INTO prj_ecoute01 (chemin__a_partir_root, root_local, root_distant, telechargee, fini, multi_easycode, table_campagne) VALUES ( '2017\11\08\15\02\500003e0aa8c000000a805a031c9006790010f3360001000101.wav', '.\ecoute_enreg\', '\\mcuci\Storage$\', '0', '0', 19240025, 'ct_NIP_2018'), ( '2017\11\08\15\02\580003e0aa8c000000a805a031c9f067c0010f33c0001000018.wav', '.\ecoute_enreg\', '\\mcuci\Storage$\', '0', '0', 19240026, 'ct_NIP_2018'), ( '2017\11\08\15\03\270003e0aa8c000000a805a031cbc06830010f34b0001000115.wav', '.\ecoute_enreg\', '\\mcuci\Storage$\', '0', '0', 19240026, 'ct_NIP_2018')
        # sys.exit(0)


        # ty tsy olana fa ilai fanamboarana anlai requete no enjana
        try:
            self.cursor_pg_local.execute(query_insert)
        except psycopg2.ProgrammingError:
            ###essaie de supprimer ceci##########################
            # self.umount_samba_server()
            self.msg_box_information(
                "Relation fichier Excel et la Campagne choisie",
                "Incoherence de table( "+ self.table_campagne01 +" ) et easycode(" + monoeasy+ ")"\
                + "\n- Erreur dans Psycopg"
            )
            self.logging_n_print(
                type_log = "warning",
                txt = "Incoherence de table( "+ self.table_campagne01 +" ) et easycode(" + monoeasy+ ")"
            )
            # sys.exit(0)
            return

        # eto ni mnw insertion
        self.connect_pg_local_saisie.commit()

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

        # elem sera un mono_easycode
        for elem in list_multieasycode:
            if (str(elem)[-2:] == ".0"):
                self.qtlist_multieasycode.\
                    addItem(str(elem)[:-2])
            else:
                self.qtlist_multieasycode.\
                    addItem(str(elem))
        ###essaie de supprimer ceci##########################
        # self.umount_samba_server()
        #fin_import_xls


    ####eto
    # asio log_file
    # # mbola lava b io... jereo we inn dol ni affichage tsara loggena
    # # ni vita farany zan d hoe: rhf mnw import_xls
    # atov ani anaty fichier_conf
    # # ti mbola ketrika hafa mitsn
    def handle_file_log(self):
        
        if (os.path.exists(self.log_file)):
            statinfo = os.stat(self.log_file)
            if statinfo.st_size > self.max_size_log:
                os.remove(self.log_file)
                open(self.log_file, 'a').close()

        print ""

    def logging_n_print(self, 
            bool01 = True,
            type_log = "info", # OU warning OU debug
            txt = "text",
            log_only = True):

        if(type_log == "warning"):
            logging.warning(txt)
            if log_only == False:
                print txt
            

        elif (type_log == "info"):
            logging.info(txt)
            if log_only == False:
                print txt

        elif ((type_log == "debug") & (log_only == False)):
            logging.debug(txt)
            if log_only == False:
                print txt

        elif ((type_log == "debug") & (log_only == True)):
            logging.debug(txt)
            if log_only == False:
                print txt

    def handle_ip_insertion(self):
        req = "SELECT EXISTS(SELECT ip FROM ecoute_ip WHERE ip LIKE '"\
            +str(self.get_ip())\
            +"')"
        self.pg_select(
            query = req,
            host = "192.168.10.5")

        # print self.rows_pg_10_5[0][0]

        if (self.rows_pg_10_5[0][0] == True):
            self.logging_n_print(
                txt = self.get_ip() + " deja present dans la BDD",
                type_log = "info")
            

        else:
            self.logging_n_print(
                txt = self.get_ip() + " insertion dans la BDD",
                type_log = "info")
            ins_req = "INSERT INTO ecoute_ip(ip) VALUES ('"+\
                self.get_ip()\
                +"')"
            self.pg_not_select(
                query01 = ins_req,
                host = "192.168.10.5")
            # print "tsy ao"

    def check_pass(self):
        # maka anlay mot_de_passe
        self.pg_select(
            query = "SELECT passw FROM pass_infodev WHERE id_pass = (SELECT MAX(id_pass) FROM pass_infodev);",
            host = "192.168.10.5")
        # print self.rows_pg_10_5[0][0]

        self.right_passw = False
        while True:
            
            self.dialog_passw = QtGui.QDialog()
            self.dialog_passw.setWindowTitle("Mot de Passe")
            self.dialog_passw.setMinimumSize(300, 50)
            qvbox_layout_dailog_passw = QtGui.QHBoxLayout(self.dialog_passw)
            self.button_ok_at_dialog_passw = QtGui.QPushButton("OK", self.dialog_passw)
            self.button_ok_at_dialog_passw.clicked.connect(self.clicked_ok_at_dialog_passw)
            self.qline_entered_passw = QLineEdit(self.dialog_passw)
            self.qline_entered_passw.setEchoMode(QLineEdit.Password)
            
            qvbox_layout_dailog_passw.addWidget(self.button_ok_at_dialog_passw)
            qvbox_layout_dailog_passw.addWidget(self.qline_entered_passw)
            self.dialog_passw.exec_()
            self.logging_n_print(type_log = "warning",
                    txt = "Tentation d'Entree dans zone Info_Dev")
            if self.qline_entered_passw.text() == self.rows_pg_10_5[0][0] :
                self.logging_n_print(type_log = "info",
                    txt = "Entree Reussite dans zone Info_Dev")
                break
            else:
                self.logging_n_print(type_log = "warning",
                    txt = "Echec d'entree dans zone Info_Dev _ MDP: " \
                        + self.qline_entered_passw.text()
                )
                pass
            if self.right_passw == True:
                self.logging_n_print(type_log = "info",
                    txt = "Entree Reussite dans zone Info_Dev")
                break
            else:
                self.logging_n_print(type_log = "warning",
                    txt = "Echec d'entree dans zone Info_Dev _ MDP: " \
                        + self.qline_entered_passw.text()
                )
                pass

        # print self.qline_entered_passw.text()

        # iti ilai rhf mnw insertion am inputdialog dia hita dol
            # while True:
                # entered_passw, ok = QtGui.QInputDialog.getText(self, 
                    # 'Mot De Passe', 
                    # 'Entrer votre Mot De Passe:')
                # if ok:
                    # print "the text which you entered is: " + entered_passw
                    # if entered_passw == self.rows_pg_10_5[0][0]:
                        # print "mtov"
                        # break
                    # else:
                        # print "Mot de Passe Incorrect"
                # else:
                    # print "you clicked cancel" 
                    # break




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
        # print "this is from the dialog"

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




    def pg_not_select(self, 
            query01,            
            host = "127.0.0.1"):
        if( host == "127.0.0.1"):
            self.cursor_pg_local.execute(query01)
            self.connect_pg_local_saisie.commit()
            # self.cursor_pg_local.close()

    def connect_pg(self, 
            server01 = '',
            user01='',
            password01='',
            database01=''):

        if (server01 == '127.0.0.1'):
            self.connect_pg_local_saisie = psycopg2.connect(
                "dbname=" + database01
                +" user=" + user01
                +" password=" + password01
                +" host=" + server01
            ) 

            self.connect_pg_local_saisie.set_isolation_level(0)

            self.cursor_pg_local = self.connect_pg_local_saisie.cursor()

            self.logging_n_print (txt = "connection ok au postgresql LOCAL")
        elif(server01 == '192.168.10.5'):
            self.connect_pg_10_5 = psycopg2.connect(
                "dbname=" + database01
                +" user=" + user01
                +" password=" + password01
                +" host=" + server01
            )
            self.connect_pg_10_5.set_isolation_level(0)

            self.cursor_pg_10_5 = self.connect_pg_10_5.cursor()

            self.logging_n_print (txt = "connection ok au postgresql 192.168.10.5")

     
            
    def addFiles(self):
        files = QtGui.QFileDialog.getOpenFileNames(self, 
            "Veuillez choisir un Fichier Audio",
            QtGui.QDesktopServices.storageLocation(
                QtGui.QDesktopServices.MusicLocation
            )
        )

        print files

        if not files:
            return

        index = len(self.sources)

        # for string in files:
            # self.sources.append(Phonon.MediaSource(string))
            
        # self.sources.append(Phonon.MediaSource(files[0]))

        if self.sources:
            self.metaInformationResolver.setCurrentSource(self.sources[index])


    


    









    # va s_exe apres choix d_un campagne
    def selection_change_combo_campagne(self):  
        
        self.etat_elemS(
            campg = True,
            multieasyc = True,
            monoeasyc = True,
            dldd = True
        )

        # print self.combo_box__campagne.currentText()
        self.etat_elemS(
            campg = True,
            multieasyc = True,
            monoeasyc = True,
            dldd = True,
            import_xls_action = True
        )
        # print "#####################################"
        # print list_call_date01
        # list_call_date01 = list(set(list_call_date01))
        # list_call_date01 = sorted(list_call_date01)
        tmp_txt = "Choix Campagne: " + self.combo_box__campagne.currentText()
        self.logging_n_print(txt = tmp_txt)

        # self.campagne__table_campagne est un dico
        # XX.get() prend un clee et la valeur correspondante
        self.table_campagne01 = str(self.campagne__table_campagne.get(
                self.combo_box__campagne.currentText()
            )
        )
        
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
        

    def about_pdf(self):
        # print "this is a test"
        os.system(".\Manuel_Interface_Ecoute.pdf")
        pass

    def about(self):
        # QtGui.QMessageBox.information(self, "About Music Player",
        #         "The Music Player example shows how to use Phonon - the "
        #         "multimedia framework that comes with Qt - to create a "
        #         "simple music player.")
        QtGui.QMessageBox.information(
                self, 

                "Outil pour Ecouter les Appels de Vivetic",

                "Outil pour Ecouter les Appels de Vivetic\n"
                "- On choisit une Campagne\n"
                "- On choisit le fichier Excel qui contient les Easycodes\n"
                "- - Tous les Easycodes du fichiers Excel vont s'afficher dans la liste\n"
                "-\n"
                "- On choisit un easycode\n"
                "- - Les Enregistrements d'appel associees au easycode choisit vont s'afficher\n"
                "- On double_clique le fichier Audio qu'on veut lire\n"
                "- On clique sur bouton(Jouer) pour le mettre dans le Playlist\n"
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

    def clicked_table_edit(self):
        print "Clicked table_edit"
        pass

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

    def clicked_ajouter_dialog(self):
        # print indexes
        indexes = self.qtable_at_dialog.selectionModel().selectedRows()
        for index in sorted(indexes):
            # print('Row %d is selected' % index.row())
            self.clicked_enreg = self.\
                list__dl_fini_chemin_easycode[index.row()][2]
            self.playlist.append(self.list__dl_fini_chemin_easycode[index.row()][2])

            chemin_enreg__local = self.root_local \
                + self.list__dl_fini_chemin_easycode[index.row()][2][-55:]

            self.add_single_song_to_playlist(
                path_audio = chemin_enreg__local
            )

        # print "playlist00212121"
        # print self.playlist


        # self.sources.append(Phonon.MediaSource('E:\\DISK_D\\ecoutes\\2017\\07\\13\\15\\44\\490003e0aa8c0000015405967956bbc9f0015b3820001000205.wav'))


        # for tmp in self.playlist:
            # self.sources.append(
                # Phonon.MediaSource(
                    # self.root_local + tmp
                # )
            # )
            # print ""
            # print self.root_local + tmp
            # self.add_single_song_to_playlist(path_audio = (self.root_local + tmp))

        print "clicked ajouter au dialog"

    def closeEvent(self, *args, **kwargs):
        ###essaie de supprimer ceci##########################
        # self.umount_samba_server()
        for i in range(3):
            self.logging_n_print(txt = "")
        self.logging_n_print(txt = "closed")
        for i in range(3):
            self.logging_n_print(txt = "")

    def to_del001(self):
        # self.dialog_passw = QtGui.QDialog()
        # flo = QFormLayout(self.dialog_passw)
        # e1 = QLineEdit()
        # self.button_ok_dialog_passw = QtGui.QPushButton(
            # "OK"
        # )
        # self.button_annuler_dialog_passw = QtGui.QPushButton(
            # "Annuler"
        # )
        # flo.addRow("Mot De Passe: ", e1)
        # flo.addRow(self.button_ok_dialog_passw)
        # flo.addRow(self.button_annuler_dialog_passw)
        # # win = QWidget()
        # # win.setLayout(flo)
        # # win.show()
        # raw_input("ato")
        # print e1.text()

        self.dialog_passw = QtGui.QDialog()
        self.dialog_passw.setMinimumSize(300, 50)
        qvbox_layout_dailog_passw = QtGui.QHBoxLayout(self.dialog_passw)
        self.button_ok_at_dialog_passw = QtGui.QPushButton("OK", self.dialog_passw)
        self.button_ok_at_dialog_passw.clicked.connect(self.clicked_ok_at_passw)
        self.qline_entered_passw = QLineEdit(self.dialog_passw)
        self.qline_entered_passw.setEchoMode(QLineEdit.Password)
        
        qvbox_layout_dailog_passw.addWidget(self.button_ok_at_dialog_passw)
        qvbox_layout_dailog_passw.addWidget(self.qline_entered_passw)
        self.dialog_passw.exec_()


    def dl_fichier (
        self,
        bool01 = True,
        remote_file01 = "\\\\mcuci\\Storage$\\2017\\07\\05\\14\\03\\050003e0aa8c000001540595cf1976568001369720001000149.wav",
        sauvegardee_dans = ".\\ato100.wav"):

        # print "clicked test"
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
            
            # cmd01 = 'smbget '\
                # + remote_file01\
                # +' '\
                # + sauvegardee_dans
                
            # sys.exit(0)
            # os.system(cmd01)
            try:
                shutil.copy(remote_file01, sauvegardee_dans)
                print "Telechargement dans: " + sauvegardee_dans
            except IOError:
                # print "ERROR"
                # print "Je vous prie de Recommencez dans quelques secondes"
                # self.msg_box_information(titre = "Erreur Temporaire",
                    # txt = r"Je vous prie de Refermer le Programme et Reessaier dans quelques secondes")
                # self.logging_n_print(type_log = "debug",
                    # txt = "Fichier Inexistant: " + remote_file01
                    # )
                #                 
                # print "fichier: " \
                # + remote_file01 \
                # + " est sauvee dans "\
                # + sauvegardee_dans

                self.logging_n_print(type_log = "debug", 
                    txt = "IOError lors du Telechargement du Fichier: " + remote_file01
                )
                self.msg_box_information("Veuillez Patienter",
                    "Téléchargement à partir du Serveur")
                ###essaie de supprimer ceci##########################
                # self.mount_samba_server()
                try:
                    shutil.copy(remote_file01, sauvegardee_dans)
                except IOError:
                    print "ooops IOError"
                finally:
                    ###essaie de supprimer ceci##########################
                    # self.umount_samba_server()
                    pass


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
        self.etat_elemS(
            campg = True,
            multieasyc = True,
            monoeasyc = True,
            dldd = True,
            import_xls_action = False
        )



    def lire_xlsx__get_call_date(self, 
            fichier_xlsx = 'E:\\DISK_D\\mamitiana\\kandra\\stuffs\\file01.xlsx',
            campgn = "0"):
        """
        va retourner les call_date qui sont reliees aa param_campgn
        """
        res_list_call_date = [] 

        print "get call_date"

        if fichier_xlsx.is_file():
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
        # print "about to finish 65654654654"
        index = self.sources.index(self.mediaObject.currentSource()) + 1
        play_finished = self.list__dl_fini_chemin_easycode[\
            self.musicTable.selectionModel().selectedRows()[0].row()\
        ][2]

        req001 = "UPDATE prj_ecoute01 SET fini = 1 "\
            +"WHERE chemin__a_partir_root = '" \
            +play_finished+"';"
        self.pg_not_select(
            query01 = req001,
            host = "127.0.0.1")


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



        # self.bouton_reinit_elemS = QtGui.QPushButton(
            # "Reinitialiser"
        # )

        self.bouton_test = QtGui.QPushButton(
            "Monter les Serveurs"
        )

        # self.bouton_reinit_elemS.clicked.connect(
            # self.remove_all_qtlist_multieasycode
            # # (
                # # text01 = "akondro"
            # # )
        # )


        self.bouton_test.clicked.connect(
            # self.dl_fichier ## bouton_test_dl
            # self.select_fichier_dl
            # self.remove_all_qtlist_multieasycode
            # self.samba_check_file
            # self.extract01  # that one is going to extract some BASIC info from sql_server
                            # # you should delete that one
            # self.umount_samba_server
            # self.lire_xlsx_campagne 
            # self.dialog_enregistrement 
            # self.del_all_sources
            # self.select_list_campagne
            # self.check_existance_pg_int
            self.add_single_song_to_playlist
            ###essaie de supprimer ceci##########################
            # self.mount_samba_server
            # self.to_del001
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
            "&Aide", 
            self, 
            shortcut="Ctrl+A",
            triggered=self.about
        )

        self.aboutActionPdf = QtGui.QAction(
            "Aide avec &PDF", 
            self, 
            shortcut="Ctrl+P",
            triggered=self.about_pdf
        )

        self.aboutQtAction = QtGui.QAction(
            "A propos de &Qt", 
            self,
            shortcut="Ctrl+Q", 
            triggered=QtGui.qApp.aboutQt
        )

        self.info_dev = QtGui.QAction(
            "Info Dev", 
            self,
            shortcut="Ctrl+M", 
            triggered=self.mount_samba_server_def
        )



    def method01(self):
        print "this is a test"

    def keyPressEvent(self, event):
    # Did the user press the Escape key?
        if event.key() == (QtCore.Qt.Key_Control and QtCore.Qt.Key_Shift \
                and QtCore.Qt.Key_M and QtCore.Qt.Key_S and QtCore.Qt.Key_N): # QtCore.Qt.Key_Escape is a value that equates to what the operating system passes to python from the keyboard when the escape key is pressed.
            # Yes: Close the window
            print "step 1"
            self.mount_samba_server_def()
        elif event.key() == (QtCore.Qt.Key_Control and QtCore.Qt.Key_Shift and QtCore.Qt.Key_I):
            print self.get_ip()
        # No:  Do nothing.


    def setupMenus(self):
        # fileMenu = self.menuBar().addMenu("&File")
        fileMenu = self.menuBar().addMenu("&Fichier")
        fileMenu.addAction(self.addFilesAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        # aboutMenu = self.menuBar().addMenu("&Help")
        aboutMenu = self.menuBar().addMenu("&Aide")
        aboutMenu.addAction(self.aboutAction)
        aboutMenu.addAction(self.aboutActionPdf)
        aboutMenu.addAction(self.aboutQtAction)
        # aboutMenu.addAction(self.info_dev)


    def long_print(self, nb_void = 5000):
        for i in range(nb_void):
            print ""

    def clicked_ok_at_passw(self):
        print "you clicked ok in the password"

    def dialog_enregistrement(self, 
            bool01 = True,
            list__dl_fini_chemin_easycode =
            [
                # dl    fini    chemin      easycode
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
        
        self.button_close_at_dialog = QtGui.QPushButton("Fermer", self.dialog01)
        # self.button_ajouter_at_dialog = QtGui.QPushButton("Ajouter", self.dialog01)

        self.button_close_at_dialog.clicked.connect(self.clicked_bouton_fermer_dialog)
        # self.button_ajouter_at_dialog.clicked.connect(self.clicked_ajouter_dialog)


        rows = len(list__dl_fini_chemin_easycode)
        cols = len(list__dl_fini_chemin_easycode[0])
        self.qtable_at_dialog = QtGui.QTableWidget(rows, cols, self.dialog01)
        self.qtable_at_dialog.setSelectionBehavior(QtGui.QTableView.SelectRows)
        

        self.dialog01.setMinimumSize(600, 50)
        self.qtable_at_dialog.setStyleSheet(
            '''
            QTableWidget { max-width: 600px; min-height: 200px;}
            '''
        )
        qvbox_layout_dialog.addWidget(self.button_close_at_dialog)
        # qvbox_layout_dialog.addWidget(self.button_ajouter_at_dialog)
        qvbox_layout_dialog.addWidget(self.qtable_at_dialog)

        # les entetes du table_dialog
        self.qtable_at_dialog.setHorizontalHeaderLabels(
            ['Download', 'Fini', 'Chemin', 'Easycode'])

        self.qtable_at_dialog\
            .doubleClicked.connect(
                self.double_clicked_qtable_at_dialog
        )

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
                    self.qtable_at_dialog.setItem(row, col, item)

                elif col == 1:
                    # Fini
                    item = QtGui.QTableWidgetItem()
                    if(list__dl_fini_chemin_easycode[row][col] == False):
                        item.setCheckState(QtCore.Qt.Unchecked)
                        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    else:
                        item.setCheckState(QtCore.Qt.Checked)
                        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    
                    self.qtable_at_dialog.setItem(row, col, item)

                elif col == 2:
                    # Chemin
                    item = QtGui.QTableWidgetItem(
                        list__dl_fini_chemin_easycode[row][col]
                    )
                    item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    self.qtable_at_dialog.setItem(row, col, item)
                elif col == 3:
                    # easycode
                    item = QtGui.QTableWidgetItem(
                        str(list__dl_fini_chemin_easycode[row][col])
                    )
                    item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    self.qtable_at_dialog.setItem(row, col, item)


        self.dialog01.setWindowTitle("Les Enregistrements")
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

        headers = ("Title", "", "", "")
        # headers = ("Title", "Titre01", "Titre02", "Titre03")

        #~ #instanciation by default

        self.bouton_reinit_source = QtGui.QPushButton(
            "Reinitialiser Playlist"
        )

        self.bouton_reinit_source.clicked.connect(
            self.del_all_sources
        )


        self.musicTable = QtGui.QTableWidget(0, 4)
        self.musicTable.setStyleSheet(
            '''
            QTableWidget { max-width: 1000px; min-height: 50px;}
            '''
            )

        self.musicTable.itemClicked.connect(self.changed_music_table)


        self.qtable_edit_enreg = QtGui.QTableWidget(0, 1) 
        self.qtable_edit_enreg.setStyleSheet(
            '''
            QTableWidget { max-width: 1000px; min-height: 100px;}
            '''
        )
        self.qtable_edit_enreg.setRowCount(5)
        self.qtable_edit_enreg.setColumnCount(2)
        self.qtable_edit_enreg_item = QtGui.QTableWidgetItem("Test001") 
        self.qtable_edit_enreg.setItem(0, 0, self.qtable_edit_enreg_item)
        self.qtable_edit_enreg.setItem(0, 1, self.qtable_edit_enreg_item)
        # self.qtable_edit_enreg.setStyleSheet(
            # '''
            # QTableWidget { max-width: 1000px; min-height: 200px;}
            # '''
        # )

        self.qtable_edit_enreg.setHorizontalHeaderLabels(headers)
        self.qtable_edit_enreg.setSelectionMode(
            QtGui.QAbstractItemView.SingleSelection
        )
        self.qtable_edit_enreg.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows
        )
        self.qtable_edit_enreg.cellPressed.connect(
            self.clicked_table_edit
        )
       

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
            QComboBox { max-width: 1000px; min-height: 20px;}
            '''
        )



        self.combo_box__campagne.addItems(
            # ["campagne01", "campagne02", "campagne03"]
            self.select_list_campagne()
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

        playbackLayout.addWidget(self.bouton_reinit_source)

        # dans _ def setupUi(self):

        self.tabwidget = QtGui.QTabWidget()

        self.tab_excel_down = QtGui.QWidget()
        self.tab_saisie_down = QtGui.QWidget()

        self.plain_txt_easycode = QtGui.QPlainTextEdit(self.tab_saisie_down)
        self.button_display_easyc_to_playlist_edit = QtGui.QPushButton(
            "Click3635689", 
            self.tab_saisie_down
        )
        
        self.button_display_easyc_to_playlist_edit.clicked.connect(
            self.take_list_easycode_to_playlist
        )
        self.button_display_easyc_to_playlist_edit.setGeometry(
            QtCore.QRect(350, 50, 150, 23))

        self.button_test002 = QtGui.QPushButton(
            "button_test", 
            self.tab_saisie_down
        )
        self.button_test002.clicked.connect( 
            self.test11515151
        )
        self.button_test002.setGeometry(
            QtCore.QRect(550, 50, 150, 23))

        self.combo_box__campagne = QtGui.QComboBox(self.tab_excel_down)
        self.combo_box__campagne.setGeometry(QtCore.QRect(50, 50, 150, 23))
        self.combo_box__campagne.setStyleSheet('''
                    QComboBox { max-width: 1000px; min-height: 20px;}
                    '''
        )
        self.combo_box__campagne.addItems(
                    # ["campagne01", "campagne02", "campagne03"]
                    self.select_list_campagne()
                )
        self.combo_box__campagne.\
                currentIndexChanged.\
                connect(
                    self.selection_change_combo_campagne
        )
        self.combo_box__campagne.setEnabled(True)
        
        self.bouton_reinit_elemS = QtGui.QPushButton(
            self.tab_excel_down
        )
        self.bouton_reinit_elemS.setText("Reinitialiser")
        self.bouton_reinit_elemS.setGeometry(QtCore.QRect(600, 50, 100, 23))
        self.bouton_reinit_elemS.clicked.connect(
            self.remove_all_qtlist_multieasycode
        )


        self.button_test = QtGui.QPushButton(self.tab_excel_down)
        self.button_test.setText('Importer Excel')
        self.button_test.clicked.connect(
            self.import_xls
        )
        self.button_test.setGeometry(QtCore.QRect(220, 50, 100, 23))

        self.qtlist_multieasycode = QtGui.QListWidget(self.tab_excel_down)
        self.qtlist_multieasycode.setGeometry(QtCore.QRect(350, 20, 200, 23))
        self.qtlist_multieasycode.setStyleSheet('''
            QListWidget { max-width: 150px; min-height: 200px;}
            '''
        )
        self.qtlist_multieasycode.addItem("")
        self.qtlist_multieasycode.\
            itemDoubleClicked.\
            connect(self.double_clicked_multieasycode)
        
        vlayout = QtGui.QVBoxLayout()
        self.tabwidget.addTab(self.tab_saisie_down, 'Saisie')
        self.tabwidget.addTab(self.tab_excel_down, 'Excel')

        vlayout.addWidget(self.tabwidget)

        # mnw anle layout

        mainLayout = QtGui.QVBoxLayout()
        qvbox_layout_music_table01 = QtGui.QHBoxLayout()
        qvbox_layout_music_table02 = QtGui.QHBoxLayout()
        layout_for_tab = QtGui.QVBoxLayout()


        # qvbox_layout_music_table01.addWidget(self.combo_box__campagne)
        # qvbox_layout_music_table01.addWidget(self.qtlist_multieasycode)
        # qvbox_layout_music_table01.addWidget(self.qtlist_monoeasycode)
        # qvbox_layout_music_table01.addWidget(self.bouton_reinit_elemS)

        mainLayout.addWidget(
            self.musicTable
        )

        mainLayout.addLayout(
            seekerLayout
        )

        mainLayout.addLayout(
            playbackLayout
        )

        mainLayout.addWidget(
            self.qtable_edit_enreg
        )

        mainLayout.addLayout(
            qhboxlayout_toolbar_play
        )  

        mainLayout.addLayout(
            qvbox_layout_music_table01
        )

        mainLayout.addLayout(
            vlayout
        )

              

        mainLayout.addLayout(
            qvbox_layout_music_table02
        )

        widget = QtGui.QWidget()
        # widget.setStyleSheet("""
           # QWidget
           # {
            # background-color: rgba(0,0,0, 50); 
            # }
            # """
        # ) 
        widget.setLayout(
            mainLayout
        )

        self.setCentralWidget(
            widget
        )

        self.setWindowTitle(
            # to_unicode("Interface d'écoute des Appels Entrants et Sortants"
            u"Interface d'Ecoute des Appels Entrants et Sortants"
        )

        # fin _ def setupUi(self):







app = QtGui.QApplication(sys.argv)
app.setApplicationName("Music Player")
app.setQuitOnLastWindowClosed(True)
app.setWindowIcon(QtGui.QIcon('headphone.png'))

window = MainWindow()

if __name__ == '__main__':
    
    window.show()

    sys.exit(app.exec_())