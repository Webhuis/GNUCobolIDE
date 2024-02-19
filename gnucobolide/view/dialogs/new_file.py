#!/usr/bin/env python3
import locale
import os
from pyqode.qt import QtCore, QtWidgets
from pyqode.core.managers import FileManager
from gnucobolide.settings import Settings
from gnucobolide.view.forms import dlg_file_type_ui


exe_template = '''      ******************************************************************
      * author:
      * date:
      * purpose:
      * tectonics: cobc
      ******************************************************************
       identification division.
       program-id. your-program-name.
       data division.
       file section.
       working-storage section.
       procedure division.
       main-procedure.
            display "hello world"
            stop run.
       end program your-program-name.

'''

module_template = '''      ******************************************************************
      * author:
      * date:
      * purpose:
      * tectonics: cobc
      ******************************************************************
       identification division.
       program-id. your-program.
       data division.
       working-storage section.
       linkage section.
       01 parametres.
           02 pa-return-code pic 99 value 0.
       procedure division using parametres.
       main-procedure.
           display "hello world"
           move 0 to pa-return-code
           stop run.
       end program your-program.
'''

templates = [exe_template, module_template, '']


exe_template_free = '''*>****************************************************************
*> author:
*> date:
*> purpose:
*> tectonics: cobc
*>****************************************************************
identification division.
program-id. your-program-name.
data division.
file section.
working-storage section.
procedure division.
main-procedure.
    display "hello world"
    stop run.
end program your-program-name.
'''

module_template_free = '''*>****************************************************************
*> author:
*> date:
*> purpose:
*> tectonics: cobc
*>*****************************************************************
identification division.
program-id. your-program.
data division.
working-storage section.
linkage section.
01 parametres.
   02 pa-return-code pic 99 value 0.
procedure division using parametres.
main-procedure.
   display "hello world"
   move 0 to pa-return-code
   stop run.
end program your-program.
'''

free_templates = [exe_template_free, module_template_free, '']


class DlgNewFile(QtWidgets.QDialog, dlg_file_type_ui.Ui_Dialog):
    """
    New file dialog. Prompts the user for a file template, a file name and
    the path were to create the file.

    To use this dialog, use the ``create_new_file`` convenience method.
    """
    def __init__(self, parent, path):
        super().__init__(parent)
        self.setupUi(self)
        self.enable_ok()
        completer = QtWidgets.QCompleter(self)
        completer.setModel(QtWidgets.QDirModel(completer))
        self.lineEditPath.setCompleter(completer)
        if not path:
            self.lineEditPath.setText(os.path.expanduser("~"))
        else:
            self.lineEditPath.setText(path)
        self.prev_pth = ""
        self.comboBoxExtension.addItems(sorted(Settings().all_extensions))
        self.comboBoxExtension.addItems(
            [ext.upper() for ext in Settings().all_extensions])

    def path(self):
        """
        Returns the path of the file to create.
        :return: new file path
        """
        return os.path.join(
            self.lineEditPath.text(),
            self.lineEditName.text() + self.comboBoxExtension.currentText())

    def template(self):
        """
        Gets the selected file template
        """
        if Settings().free_format:
            return FREE_TEMPLATES[self.comboBoxType.currentIndex()]
        else:
            return TEMPLATES[self.comboBoxType.currentIndex()]

    @QtCore.Slot(str)
    def on_lineEditName_textChanged(self, txt):
        self.enable_ok()

    @QtCore.Slot(str)
    def on_lineEditPath_textChanged(self, txt):
        self.enable_ok()

    @QtCore.Slot()
    def on_toolButton_clicked(self):
        ret = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Choose the program directory',
            Settings().last_path)
        if ret:
            self.lineEditPath.setText(ret)

    def enable_ok(self):
        pth = str(self.lineEditPath.text())
        bt = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        name = self.lineEditName.text()
        enable = name != "" and os.path.exists(pth) and os.path.isdir(pth)
        bt.setEnabled(enable)
        self.prev_pth = pth

    @classmethod
    def create_new_file(cls, parent, path=None):
        """
        Creates a new file. Shows the new file dialog and creates the file
        on disk if the dialog has been accepted and the destination does not
        overwrite any file (or the user choose to overwrite existing file).

        :param parent: Parent widget
        :return: Path or None if the dialog has been cancelled.

        """
        dlg = cls(parent, path=path)
        if dlg.exec_() == dlg.Accepted:
            path = dlg.path()
            if os.path.exists(path):
                answer = QtWidgets.QMessageBox.question(
                    parent, 'Overwrite file',
                    'The file %s already exists. '
                    'Do you want to overwrite it?' % path,
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No)
                if answer == QtWidgets.QMessageBox.No:
                    return None
            eol = FileManager.EOL.string(Settings().preferred_eol)
            text = eol.join(dlg.template().splitlines()) + eol
            data = text.encode(locale.getpreferredencoding())
            with open(path, 'wb') as f:
                f.write(data)
            return path
        return None
