from zope import schema
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('hejasverige.clubimport')

from Products.statusmessages.interfaces import IStatusMessage
from plone.directives import form
from z3c.form import field
from z3c.form import button
from hejasverige.clubimport.read import import_clubs

#from z3c.form import form, field


class IImportForm(form.Schema):

    file_to_import = schema.TextLine(
        title=_(u'Filename'),
        description=_(u'Filename to import.'),
        required=True)

    dest_folder = schema.TextLine(
        title=_(u'Destination'),
        description=_(u'Destination folder'),
        required=True)


class ImportForm(form.Form):

    fields = field.Fields(IImportForm)
    ignoreContext = True

    def updateWidgets(self):
        super(ImportForm, self).updateWidgets()

    @button.buttonAndHandler(u'Import')
    def handleImport(self, action):
        data, errors = self.extractData()
        if errors:
            return False

        if data['file_to_import'] is not None:
            file_to_import = data['file_to_import']
            dest_folder = data['dest_folder']
            import_clubs(self, file_to_import, dest_folder)

        IStatusMessage(self.request).addStatusMessage(
            "File %s imported. See log-file for more details." % file_to_import,
            'info')
        redirect_url = "%s/@@import_form" % self.context.absolute_url()
        self.request.response.redirect(redirect_url)

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            "Nothing imported...",
            'info')
        redirect_url = "%s/@@import_form" % self.context.absolute_url()
        self.request.response.redirect(redirect_url)

from plone.z3cform.layout import wrap_form
ImportFormView = wrap_form(ImportForm)
