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

        if 'file_to_import' in data:
            import_clubs(self, data['file_to_import'])

        IStatusMessage(self.request).addStatusMessage(
            "File %s imported. See log-file for more details." % data['file_to_import'],
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
