from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Project.main_ui import Ui_MainWindow
from Project.image_window import Ui_MainWindow as Ui_MainWindow_1

import Project.backend
import Project.hough_circle
import Project.homomorphic
import Project.add_circle
import Project.modify_circle

from pathlib import Path
import os
import cv2

relative_paths = []
sub_survey_paths = []
image_list = []
image_index = None
default_path = "C:/"
pmap = None
qimg = QImage()


class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.toolButton.clicked.connect(self.select_path)
        self.ui.toolButton_2.clicked.connect(self.select_sub_survey_path)
        self.ui.preProcessedCheckBox.stateChanged.connect(self.populate_survey_name)

        self.ui.newSurveyPathLineEdit.textChanged.connect(self.select_name)
        self.ui.newSubSurveyPathLineEdit.textChanged.connect(self.select_name)
        self.ui.pushButton_2.clicked.connect(self.new_survey)
        self.ui.pushButton_4.clicked.connect(self.new_sub_survey)
        self.ui.surveyComboBox.currentIndexChanged.connect(self.populate_sub_survey_name)
        self.ui.imageListWidget.currentItemChanged.connect(self.choose_image)
        self.ui.listButton.clicked.connect(self.populate_image_and_text)

        self.ui.surveyComboBox.activated.connect(self.show_descriptions)
        self.ui.subSurveyComboBox.activated.connect(self.show_descriptions)

        # vizsgálat tab

        self.ui.surveyListWidget.itemClicked.connect(self.select_survey)
        self.ui.deleteSurveyButton.clicked.connect(self.delete_survey)
        self.ui.modifySurveyDescriptionButton.clicked.connect(self.modifiy_survey_descripiton)

        # tab ss

        self.ui.parentSurveyComboBox.activated.connect(self.list_sub_survey)
        self.ui.subSurveyListWidget.itemClicked.connect(self.select_sub_survey)
        self.ui.deleteSubSurveyButton.clicked.connect(self.delete_sub_survey)
        self.ui.modifySubSurveyDescriptionButton.clicked.connect(self.modifiy_sub_survey_descripiton)

        # detektálás tab

        self.ui.tabWidget.currentChanged.connect(self.change_tabs)
        self.ui.pushButton_3.clicked.connect(self.manage_selection)
        self.ui.pushButton_7.clicked.connect(self.manage_selection)
        self.ui.pushButton_8.clicked.connect(self.manage_selection)
        self.ui.detectAndDrawButton.clicked.connect(self.finalize_selection)
        self.ui.homomorphicButton.clicked.connect(self.finalize_selection)
        self.ui.drawButton.clicked.connect(self.circle_edge)
        self.ui.modifyButton.clicked.connect(self.circle_edge)


    def initialize_controller_gui(self):

        #self.setWindowTitle("Keretrendszer zebrahal embriók mikroszkópos képeinek feldolgozásához")
        self.setGeometry(50, 50, 400, 800)
        self.ui.newSurveyDescriptionTextEdit.setPlaceholderText("Adjon meg egy leírást a vizsgálathoz")
        self.ui.newSubSurveyDescriptionTextEdit.setPlaceholderText("Adjon meg egy leírást a részvizsgálathoz")
        self.ui.surveyTextEdit.setReadOnly(True)
        self.ui.subSurveyTextBox.setReadOnly(True)
        self.ui.imageListWidget.setViewMode(QListView.IconMode)
        self.ui.imageListWidget.setIconSize(QSize(90, 90))
        self.ui.imageListWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.imageListWidget_2.setViewMode(QListView.IconMode)
        self.ui.imageListWidget_2.setIconSize(QSize(90, 90))
        self.ui.imageListWidget_2.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ui.preProcessedCheckBox.setChecked(False)
        self.populate_survey_name()
        self.populate_sub_survey_name()
        self.list_survey()
        self.list_sub_survey()

#   Képek tab
#   (részvizsgálatok érinti)

    def populate_survey_name(self):
        self.ui.parentSurveyComboBox.clear()
        self.ui.surveyComboBox.clear()
        data = Project.backend.select_survey_names()
        sorted_list = []
        sorted_list_pp = []
        global relative_paths
        for i in range(len(data)):
            (path, name, preproc) = data[i]
            relative_paths.append(path)
            if preproc == 0:
                sorted_list.append(name)
            elif preproc == 1:
                sorted_list_pp.append(name)

        sorted_list.sort()
        sorted_list_pp.sort()
        if not sorted_list:
            if not sorted_list_pp:
                self.ui.surveyComboBox.setEditable(True)
                self.ui.parentSurveyComboBox.setEditable(True)
                self.ui.surveyComboBox.setCurrentText("Nincs vizsgálat")
                self.ui.parentSurveyComboBox.setCurrentText("Nincs vizsgálat")
        else:
            if self.ui.preProcessedCheckBox.isChecked():
                self.ui.surveyComboBox.setEditable(False)
                for item in sorted_list_pp:
                    self.ui.surveyComboBox.addItem(item)
            else:
                self.ui.surveyComboBox.setEditable(False)
                for item in sorted_list:
                    self.ui.surveyComboBox.addItem(item)
            merged_list = sorted_list + sorted_list_pp
            self.ui.parentSurveyComboBox.setEditable(False)

            for item in merged_list:
                self.ui.parentSurveyComboBox.addItem(item)

    def populate_sub_survey_name(self):
        self.ui.subSurveyComboBox.clear()
        name = self.ui.surveyComboBox.currentText()
        data = Project.backend.select_sub_survey_names(name)
        sorted_list = []
        global sub_survey_paths
        for i in range(len(data)):
            (path, name, parent_name, preproc) = data[i]
            sub_survey_paths.append(path)
            sorted_list.append(name)
        sorted_list.sort()
        if not sorted_list:
            self.ui.subSurveyComboBox.setEditable(True)
            self.ui.subSurveyComboBox.setCurrentText("Nincs részvizsgálat")
        else:
            self.ui.subSurveyComboBox.setEditable(False)
            for item in sorted_list:
                self.ui.subSurveyComboBox.addItem(item)

    def show_descriptions(self):
        qm = QMessageBox()
        self.ui.listButton.setEnabled(True)
        sender = self.sender()
        if sender.objectName() == "surveyComboBox":
                self.ui.surveyTextEdit.clear()
                survey_p = self.ui.surveyComboBox.currentText()
                da = Project.backend.select_survey_path(survey_p)
                for i in range(len(da)):
                    (name, path, preproc) = da[i]
                    cupath = name
                    txt_file_name = path
                survey_description = cupath + "/" + txt_file_name + ".txt"
                if os.path.isfile(survey_description):
                    contents = Project.backend.read_file(survey_description)
                    self.ui.surveyTextEdit.append(contents)
                else:
                    QMessageBox.about(qm, "Sikertelen", "Ehhez az elérési útvonalhoz már nem tartozik vizsgálat")
                    self.ui.listButton.setEnabled(False)
        if sender.objectName() == "subSurveyComboBox":
                self.ui.subSurveyTextBox.clear()
                path = self.ui.subSurveyComboBox.currentText()
                data = Project.backend.select_sub_survey_path(path)
                for i in range(len(data)):
                    (name, path, parentname, preproc) = data[i]
                    crpath = name
                    text_file_name = path
                sub_survey_description = crpath + "/" + text_file_name + ".txt"
                if os.path.isfile(sub_survey_description):
                    content = Project.backend.read_file(sub_survey_description)
                    self.ui.subSurveyTextBox.append(content)
                else:
                    QMessageBox.about(qm, "Sikertelen", "Ehhez az elérési útvonalhoz már nem tartozik részvizsgálat")
                    self.ui.listButton.setEnabled(False)

    def populate_image_and_text(self):
        if self.ui.surveyComboBox.currentText() == "Nincs vizsgálat" or self.ui.subSurveyComboBox.currentText() == \
                "Nincs részvizsgálat":
            qm = QMessageBox()
            QMessageBox.about(qm, "Sikertelen", "Nincsenek megjeleníthető vizsgálatok/részvizsgálatok")
        else:
            #self.ui.surveyTextEdit.clear()
            #self.ui.subSurveyTextBox.clear()
            self.ui.imageListWidget.clear()
            spath = self.ui.surveyComboBox.currentText()
            da = Project.backend.select_survey_path(spath)
            for i in range(len(da)):
                (name, path, preproc) = da[i]
                cupath = name
                txt_file_name = path
            survey_description = cupath + "/" + txt_file_name + ".txt"
            contents = Project.backend.read_file(survey_description)
            #self.ui.surveyTextEdit.append(contents)
            sspath = self.ui.subSurveyComboBox.currentText()
            data = Project.backend.select_sub_survey_path(sspath)
            for i in range(len(data)):
                (name, path, parentname, preproc) = data[i]
                cpath = name
                text_file_name = path
            sub_survey_description = cpath + "/" + text_file_name + ".txt"
            content = Project.backend.read_file(sub_survey_description)
            #self.ui.subSurveyTextBox.append(content)
            global image_list
            image_list.clear()
            for ffile in os.listdir(cpath):
                if ffile.endswith(".JPG"):
                    #image_list.append(os.path.join(cpath, ffile))
                    image_list.append(cpath + "/" + ffile)

        for x in image_list:
            item = QListWidgetItem()
            font = QFont()
            font.setPixelSize(5)
            icon = QIcon()
            icon.addPixmap(QPixmap(x), QIcon.Normal, QIcon.Off)
            item.setIcon(icon)
            item.setText(x.split("/")[-1])
            item.setFont(font)
            self.ui.imageListWidget.addItem(item)
            item = QListWidgetItem()
            font = QFont()
            font.setPixelSize(5)
            icon = QIcon()
            icon.addPixmap(QPixmap(x), QIcon.Normal, QIcon.Off)
            item.setIcon(icon)
            item.setText(x.split("/")[-1])
            item.setFont(font)
            self.ui.imageListWidget_2.addItem(item)

    def choose_image(self):
        global image_list
        global image_index
        sender = self.sender()
        if self.ui.tabWidget.currentIndex() == 0:
            if image_list:
                if sender.objectName() == 'imageListWidget':
                    image_index = self.ui.imageListWidget.currentRow()
                elif sender.objectName() == 'previousButton':
                    image_index = self.ui.imageListWidget.currentRow() - 1
                    self.ui.imageListWidget.setCurrentRow(image_index)
                elif sender.objectName() == 'nextButton':
                    image_index = self.ui.imageListWidget.currentRow() + 1
                    self.ui.imageListWidget.setCurrentRow(image_index)
                elif sender.objectName() == 'submitButton':
                    image_index = self.ui.imageListWidget.currentRow()
                    self.create_comment(image_list[image_index])

                current_image = image_list[image_index]
                self.show_image(current_image)
                image_window.setWindowTitle(current_image.split("/")[-1])
            else:
                qm = QMessageBox()
                QMessageBox.about(qm, "Sikertelen", "Nincsenek megjeleníthető képek")

    def show_image(self, image):
        global pmap
        if self.ui.tabWidget.currentIndex() == 0:
            image_window.gui.imageDesciriptionTextEdit.clear()
            image_window.gui.StatusComboBox.setCurrentIndex(0)
            img = cv2.imread(image, cv2.IMREAD_COLOR)
            qimg = QImage(img.data, img.shape[1], img.shape[0], (img.shape[1])*3, QImage.Format_RGB888).rgbSwapped()
            pmap = QPixmap(qimg)
            smaller_pixmap = pmap.scaled((img.shape[0])/10*7, (img.shape[1])/10*7, Qt.KeepAspectRatio, Qt.FastTransformation)
            image_window.gui.imageLabel.setPixmap(smaller_pixmap)
            image_window.gui.imageLabel.setPixmap(smaller_pixmap)
            image_window.gui.resizeSlider.setValue(7)

        if window.ui.preProcessedCheckBox.isChecked():
            pieces = image.split(".")
            darabok = pieces[0].split("/")
            del(darabok[-2])
            image_name = darabok[-1].split("_")[0]
            del(darabok[-1])
            crt_txt = ""
            for i in range(len(darabok)):
                crt_txt += darabok[i] + "/"
            crt_txt += image_name
            current_txt = Path(crt_txt + ".txt")
        else:
            pieces = image.split(".")
            current_txt = Path(pieces[0] + ".txt")
        if current_txt.is_file():
            content = Project.backend.read_file(current_txt)
            lastline = content.split("\n")[-1].lower()
            if "<" in lastline and ">" in lastline:
                if "nincs vályú" in lastline:
                    image_window.gui.StatusComboBox.setCurrentIndex(1)
                elif "nincs embrió" in lastline:
                    image_window.gui.StatusComboBox.setCurrentIndex(2)
                elif "nem kelt ki" in lastline:
                    image_window.gui.StatusComboBox.setCurrentIndex(3)
                elif "nem élő" in lastline:
                    image_window.gui.StatusComboBox.setCurrentIndex(4)
                elif "több embrió" in lastline:
                    image_window.gui.StatusComboBox.setCurrentIndex(5)
            image_window.gui.imageDesciriptionTextEdit.setText(content)

        image_window.show()

    def create_comment(self, image):
        if(window.ui.preProcessedCheckBox.isChecked()):
            pieces = image.split(".")
            darabok = pieces[0].split("/")
            del(darabok[-2])
            image_name = darabok[-1].split("_")[0]
            del(darabok[-1])
            crt_txt = ""
            for i in range(len(darabok)):
                crt_txt += darabok[i] + "/"
            crt_txt += image_name
            current_txt = Path(crt_txt + ".txt")
        else:
            pieces = image.split(".")
            current_txt = Path(pieces[0] + ".txt")
        crnt_text = open(current_txt, 'w+')
        content = image_window.gui.imageDesciriptionTextEdit.toPlainText()
        splices = content.split("\n")
        if "<" in splices[-1] and ">" in splices[-1]:
            if image_window.gui.StatusComboBox.currentText() != "Nem meghatározott":
                lines = splices[:-1]
                glued = "\n".join(lines)
                content = glued + "\n< " + image_window.gui.StatusComboBox.currentText() + " >"
        else:
            if image_window.gui.StatusComboBox.currentText() != "Nem meghatározott":
                content = content + "\n< " + image_window.gui.StatusComboBox.currentText() + " >"
        crnt_text.write(content)
        crnt_text.close()

    def change_tabs(self):
        if self.ui.tabWidget.currentIndex() == 3:
            self.ui.imageListWidget.setSelectionMode(QAbstractItemView.MultiSelection)
            self.ui.imageListWidget_2.clearSelection()
            self.ui.imageListWidget.clearSelection()
            image_window.close()
        elif self.ui.tabWidget.currentIndex() == 0:
            image_window.close()
            self.populate_survey_name()
            self.populate_survey_name()
            self.ui.imageListWidget_2.clear()
            self.ui.imageListWidget.clearSelection()
            self.ui.imageListWidget_2.clearSelection()
            self.ui.imageListWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        else:
            self.ui.imageListWidget.clearSelection()
            self.ui.imageListWidget_2.clearSelection()
            self.ui.imageListWidget.setSelectionMode(QAbstractItemView.SingleSelection)
            image_window.close()

        # vizsgálat tab

    def list_survey(self):
        self.ui.surveyListWidget.clear()
        data = Project.backend.select_survey_names()
        names = []
        for i in range(len(data)):
            (path, name, preproc) = data[i]
            names.append(name)
        sorted_names = names
        sorted_names.sort()
        self.ui.surveyListWidget.addItems(names)

    def new_survey(self):
        path = self.ui.newSurveyPathLineEdit.text()
        name = self.ui.newSurveyNameLineEdit.text()
        qm = QMessageBox()

        if Project.backend.insert_survey(path, name, 0):
            text_file = Path(path + '/' + name + '.txt')
            file = open(text_file, 'w+')
            content = self.ui.newSurveyDescriptionTextEdit.toPlainText()
            file.write(content)
            file.close()
            self.populate_survey_name()
            self.list_survey()
            QMessageBox.about(qm, "Sikeres rögzítés", "Sikerült a vizsgálat felvétele")
        else:
            QMessageBox.about(qm, "Sikertelen rögzítés", "Már létezik a megadott nevű vizsgálat")

    def select_survey(self):
        name = self.ui.surveyListWidget.currentItem().text()
        data = Project.backend.select_survey_path(name)
        for i in range(len(data)):
            (path, name, preproc) = data[i]
            self.ui.newSurveyPathLineEdit.setText(path)
            self.ui.newSurveyNameLineEdit.setText(name)

        survey_description = path + "/" + name + ".txt"
        if os.path.isfile(survey_description):
            self.ui.newSurveyDescriptionTextEdit.clear()
            contents = Project.backend.read_file(survey_description)
            self.ui.newSurveyDescriptionTextEdit.append(contents)

    def delete_survey(self):
        if self.ui.newSurveyPathLineEdit.text():
            qm = QMessageBox()
            qm.setText("Biztos benne hogy törli a kiválasztott vizsgálatot?")
            qm.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = qm.exec_()
            if retval == 1024:
                self.s_deletion()
        else:
            qm = QMessageBox()
            QMessageBox.about(qm, "Sikertelen törlés", "Válassza ki a törölni kívánt vizsgálatot")

    def s_deletion(self):
        name = self.ui.newSurveyNameLineEdit.text()
        Project.backend.delete_survey(name)
        Project.backend.delete_attached_sub_surveys(name)
        self.populate_survey_name()
        path = self.ui.newSurveyPathLineEdit.text()
        text_path = path + "/" + name + ".txt"
        os.remove(text_path)
        self.ui.newSurveyNameLineEdit.clear()
        self.ui.newSurveyPathLineEdit.clear()
        self.ui.newSurveyDescriptionTextEdit.clear()
        self.list_survey()

    def modifiy_survey_descripiton(self):
        name = self.ui.newSurveyNameLineEdit.text()
        path = self.ui.newSurveyPathLineEdit.text()
        text_path = path + "/" + name + ".txt"
        new_content = self.ui.newSurveyDescriptionTextEdit.toPlainText()
        Project.backend.write_file(text_path, new_content)

    def select_path(self):
        qf = QFileDialog()
        qf.setFileMode(QFileDialog.DirectoryOnly)
        global default_path
        path = QFileDialog.getExistingDirectory(qf, "Útvonal megadása", default_path)
        if path:
            self.ui.newSurveyPathLineEdit.setText(path)
            self.ui.newSurveyDescriptionTextEdit.clear()

    # részvizsgálta tab

    def list_sub_survey(self):
        self.ui.subSurveyListWidget.clear()
        data = Project.backend.select_sub_survey_names(self.ui.parentSurveyComboBox.currentText())
        names = []
        for i in range(len(data)):
            (path, name, parentname, preproc) = data[i]
            names.append(name)

        sorted_names = names
        sorted_names.sort()
        self.ui.subSurveyListWidget.addItems(sorted_names)
        self.ui.newSubSurveyNameLineEdit.clear()
        self.ui.newSubSurveyPathLineEdit.clear()
        self.ui.newSubSurveyDescriptionTextEdit.clear()


    def select_name(self):
        sender = self.sender()
        if sender.objectName() == "newSurveyPathLineEdit":
            current_path = self.ui.newSurveyPathLineEdit.text()
            pieces = current_path.split("/")
            name = pieces[-1]
            self.ui.newSurveyNameLineEdit.setText(name)
        if sender.objectName() == "newSubSurveyPathLineEdit":
            current_path = self.ui.newSubSurveyPathLineEdit.text()
            pieces = current_path.split("/")
            name = pieces[-1]
            self.ui.newSubSurveyNameLineEdit.setText(name)

    def new_sub_survey(self):
        path = self.ui.newSubSurveyPathLineEdit.text()
        name = self.ui.newSubSurveyNameLineEdit.text()
        parent = self.ui.parentSurveyComboBox.currentText()
        qm = QMessageBox()

        if Project.backend.insert_sub_survey(path, name, parent, 0):
            text_file = Path(path + '/' + name + '.txt')
            file = open(text_file, 'w+')
            content = self.ui.newSubSurveyDescriptionTextEdit.toPlainText()
            file.write(content)
            file.close()
            QMessageBox.about(qm, "Sikeres rögzítés", "Sikerült a részvizsgálat felvétele")
            self.list_sub_survey()
        else:
            QMessageBox.about(qm, "Sikertelen rögzítés", "A megadott névvel már létezik részvizsgálat")

    def select_sub_survey(self):
        name = self.ui.subSurveyListWidget.currentItem().text()
        data = Project.backend.select_sub_survey_path(name)
        for i in range(len(data)):
            (path, name, parentname, preproc) = data[i]
            self.ui.newSubSurveyPathLineEdit.setText(path)
            self.ui.newSubSurveyNameLineEdit.setText(name)

        sub_survey_description = path + "/" + name + ".txt"
        if os.path.isfile(sub_survey_description):
            self.ui.newSubSurveyDescriptionTextEdit.clear()
            contents = Project.backend.read_file(sub_survey_description)
            self.ui.newSubSurveyDescriptionTextEdit.append(contents)

    def delete_sub_survey(self):
        if self.ui.newSubSurveyPathLineEdit.text():
            qm = QMessageBox()
            qm.setIcon(QMessageBox.Critical)
            qm.setText("Biztos benne hogy törli a kiválasztott részvizsgálatot?")
            qm.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = qm.exec_()
            if retval == 1024:
                self.ss_deletion()
        else:
            qm = QMessageBox()
            QMessageBox.about(qm, "Sikertelen törlés", "Válassza ki a törölni kívánt részvizsgálatot")

    def ss_deletion(self):
        name = self.ui.newSubSurveyNameLineEdit.text()
        Project.backend.delete_sub_survey(name)
        path = self.ui.newSubSurveyPathLineEdit.text()
        text_path = path + "/" + name + ".txt"
        os.remove(text_path)
        self.ui.newSubSurveyNameLineEdit.clear()
        self.ui.newSubSurveyPathLineEdit.clear()
        self.ui.newSubSurveyDescriptionTextEdit.clear()
        self.list_sub_survey()

    def modifiy_sub_survey_descripiton(self):
        name = self.ui.newSubSurveyNameLineEdit.text()
        path = self.ui.newSubSurveyPathLineEdit.text()
        text_path = path + "/" + name + ".txt"
        new_content = self.ui.newSubSurveyDescriptionTextEdit.toPlainText()
        Project.backend.write_file(text_path, new_content)

    def select_sub_survey_path(self):
        qf = QFileDialog()
        qf.setFileMode(QFileDialog.DirectoryOnly)
        global relative_paths
        survey_name = self.ui.parentSurveyComboBox.currentText()
        data = Project.backend.select_survey_path(survey_name)
        for i in range(len(data)):
            (path, name, preproc) = data[i]
        current_path = path
        sub_survey_path = QFileDialog.getExistingDirectory(qf, "Útvonal megadása", current_path)
        if sub_survey_path:
            self.ui.newSubSurveyPathLineEdit.setText(sub_survey_path)
            self.ui.newSubSurveyDescriptionTextEdit.clear()

    # előfeldolgozás tab

    def manage_selection(self):
        all_items = self.ui.imageListWidget_2.findItems('*', Qt.MatchWildcard)
        sender = self.sender()
        if sender.objectName() == "pushButton_3":
            for i in range(len(all_items)):
                if not all_items[i].isSelected():
                    all_items[i].setSelected(True)
                else:
                    all_items[i].setSelected(False)
        if sender.objectName() == "pushButton_7":
            for i in range(len(all_items)):
                all_items[i].setSelected(True)
        if sender.objectName() == "pushButton_8":
            for i in range(len(all_items)):
                all_items[i].setSelected(False)

    def finalize_selection(self):
        sender = self.sender()
        selected_items = self.ui.imageListWidget_2.selectedItems()
        current_survey_name = self.ui.surveyComboBox.currentText()
        current_sub_survey_name = self.ui.subSurveyComboBox.currentText()

        survey_data = Project.backend.select_survey_path(current_survey_name)
        for i in range(len(survey_data)):
            (path, name, preproc) = survey_data[i]
            cpath = path
            txt_file_name = name
        survey_description = cpath + "/" + txt_file_name + ".txt"
        contents = Project.backend.read_file(survey_description)
        modified_survey_content = contents + "\nA vizsgálat előfeldolgozott változata"
        modified_survey_txt_file_name = txt_file_name + "_EF"
        modified_survey_description = cpath + "/" + modified_survey_txt_file_name + ".txt"
        if not os.path.exists(modified_survey_description):
            Project.backend.insert_survey(cpath, modified_survey_txt_file_name, 1)
            Project.backend.write_file(modified_survey_description, modified_survey_content)

        sub_survey_data = Project.backend.select_sub_survey_path(current_sub_survey_name)
        for i in range(len(sub_survey_data)):
            (path, name, parent_name, preproc) = sub_survey_data[i]
            cupath = path
            text_file_name = name

        modified_sub_survey_path = cupath + "/Elofeldolgozott"
        sub_survey_description = cupath + "/" + text_file_name + ".txt"
        scontents = Project.backend.read_file(sub_survey_description)
        modified_sub_survey_content = scontents + "\nA részvizsgálat előfeldolgozott változata"
        modified_sub_survey_txt_file_name = text_file_name + "_EF"

        modified_sub_survey_description = modified_sub_survey_path + "/" + modified_sub_survey_txt_file_name + ".txt"

        if not os.path.exists(modified_sub_survey_path):
            os.makedirs(modified_sub_survey_path)
            Project.backend.insert_sub_survey(modified_sub_survey_path, modified_sub_survey_txt_file_name
                                              , modified_survey_txt_file_name, 1)
            Project.backend.write_file(modified_sub_survey_description, modified_sub_survey_content)

        images_list = []
        for images in os.listdir(modified_sub_survey_path):
            if images.endswith(".JPG"):
                images_list.append(images)
        selected_list = []
        for i in range(len(selected_items)):
            selected_list.append(selected_items[i].text())
        intersection = (set(images_list) & set(selected_list))
        final_selection = [x for x in selected_list if x not in images_list]


        if sender.objectName() == "detectAndDrawButton":
            for i in final_selection:
                current_image = cupath + "/" + i
                final_image = modified_sub_survey_path + "/" + i.split(".")[0] + "_houghcircle" + ".JPG"

                Project.hough_circle.hc_detect(current_image, final_image)
        if sender.objectName() == 'homomorphicButton':
            for i in final_selection:
                cur = cupath + "/" + i
                fin = modified_sub_survey_path + "/" + i.split(".")[0]
                fina = fin + "_homomorphic" + ".JPG"
                Project.homomorphic.hom_filter(cur, fina)

    def circle_edge(self):
        selected_item = self.ui.imageListWidget_2.selectedItems()
        p = self.ui.subSurveyComboBox.currentText()
        data = Project.backend.select_sub_survey_path(p)
        for i in range(len(data)):
            (path, name, parent_name, preproc) = data[i]
            cupath = path
        image = cupath + "/" + selected_item[0].text()

        sender = self.sender()

        if len(selected_item) != 1:
            pass
        else:
            if sender.objectName() == "drawButton":
                Project.add_circle.give_name(image)
            if sender.objectName() == "modifyButton":
                base_sep = image.rfind('_')
                base = image[0:base_sep] + ".JPG"
                fn = ""
                name = base.split("/")
                for i in name:
                    if i != base.split("/")[-1] and i != "Elofeldolgozott":
                        if fn == "":
                            fn = fn + i
                        else:
                            fn = fn + "/" + i
                    else:
                        continue
                fullname = fn + "/" + base.split("/")[-1]
                im = image
                Project.modify_circle.give_name(im, fullname)

    '''def radius_check(self):
        selected_items = self.ui.imageListWidget_2.selectedItems()
        current_sub_survey_name = self.ui.subSurveyComboBox.currentText()
        sub_survey_data = Project.backend.select_sub_survey_path(current_sub_survey_name)
        for i in range(len(sub_survey_data)):
            (path, name, parent_name, preproc) = sub_survey_data[i]
            cupath = path
        selected_list = []
        for i in range(len(selected_items)):
            selected_list.append(selected_items[i].text())
        radius_list = []
        for i in selected_list:
            img_path = cupath + "/" + i
            radius_list.append(img_path)
        list = Project.hough_circle.hc_avarage(radius_list)
        for n in range(len(list)):
            list[n] = list[n] * 2
        sorted_r = list
        sorted_r.sort()
        for i in range(len(sorted_r)):
            if sorted_r[i] == 0:
                continue
            else:
                min_r = sorted_r[i]
                break
        max_r = sorted_r[-1]
        sum = 0
        for i in list:
            sum = sum + i
        avg = sum / len(list)
        avg = int(avg)'''

    def resize_image(self):
        global pmap
        height = 1388
        width = 1040

        multiplier = image_window.gui.resizeSlider.value()
        resized_pixmap = pmap.scaled(height/10*multiplier, width/10*multiplier, Qt.KeepAspectRatio, Qt.FastTransformation)
        image_window.gui.imageLabel.setPixmap(resized_pixmap)


class ImgWindow(QMainWindow):

    def __init__(self):
        super(ImgWindow, self).__init__()

        self.gui = Ui_MainWindow_1()
        self.gui.setupUi(self)
        self.setGeometry(500, 50, 800, 800)

        self.gui.previousButton.clicked.connect(window.choose_image)
        self.gui.nextButton.clicked.connect(window.choose_image)
        self.gui.submitButton.clicked.connect(window.choose_image)
        self.gui.resizeSlider.valueChanged.connect(window.resize_image)
        self.gui.frame_3.setMinimumSize(832, 624)


if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('Fusion')
    window = MyWindow()
    window.show()
    image_window = ImgWindow()
    Project.backend.create_tables()
    window.initialize_controller_gui()
    app.exec_()
