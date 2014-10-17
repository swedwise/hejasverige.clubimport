# -*- coding: utf-8 -*-

from lxml import etree 
from plone.dexterity.utils import createContent
from plone.dexterity.utils import addContentToContainer
import transaction
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.interfaces import INamedFileField
from plone.namedfile.interfaces import INamedImageField
import mimetypes
from zope.schema import getFields
from hejasverige.content.sports.interfaces import IClub
import os

LOG_FILE = open('./log.txt', 'w')

def log(s):
    #import sys
    print >>LOG_FILE, s

def set_field():
    # Get the field containing data
    '''
    fields = getFieldsInOrder(IInvoice)
    file_fields = [field for name, field in fields
                   if INamedFileField.providedBy(field)
                   or INamedImageField.providedBy(field)
                   ]
    for file_field in file_fields:
        if IPrimaryField.providedBy(file_field):
            break
        else:
            # Primary field can't be set ttw,
            # then, we take the first one
            file_field = file_fields[0]

    value = NamedBlobFile(data=invoicefile,
                          contentType=contenttype,
                          filename=unicode(filename, 'utf-8'))

    file_field.set(content, value)

    folder = self.context['invoices']
    '''

def try_add_district(district):
    from Products.CMFPlone.utils import safe_unicode
    print 'Found district', district.get('name')
    #districtfolder.allowedContentTypes()[0].id
    district_obj = createContent(portal_type='hejasverige.District',
                                 title=safe_unicode(district.get('name')),
                                 districtId=safe_unicode(district.get('id')),
                                )
    try:
        item = addContentToContainer(container=district.get('context'), object=district_obj, checkConstraints=False)
    except Exception, ex:
        print 'Problem when importing district ', district_obj.title, 'due to', str(ex)
        log(str(ex))
        #import pdb; pdb.set_trace()
        return None
    return item

def try_add_council(council):
    council_obj = createContent(portal_type='hejasverige.Council',
                                 title=unicode(council.get('name')),
                                 councilId=unicode(council.get('id')),
                                )
    try:
        item = addContentToContainer(container=council.get('context'), object=council_obj, checkConstraints=False)
    except Exception, ex:
        print 'Problem when importing council', council_obj.title, 'due to', str(ex)
        log(str(ex))
        #import pdb; pdb.set_trace()
        return None
    return item

def try_add_club(club, basepath):
    '''
            <Name>Älvdalens SKG</Name>
            <Sport>Skidskytte</Sport>
            <href>http://www.idrottonline.se/alvdalen/alvdalensskg-skidskytte</href>
            <href2>alvdalensskg-skidskytte</href2>
            <ImagePath>/ImageVaultFiles/id_24430/cf_88/st_edited/B_jYai2SapohufBMN0Ct.jpg</ImagePath>
            <Info>
              <Key name="Bildad">[saknas] </Key>
              <Key name="Föreningsnummer">4640-59</Key>
              <Key name="Adress">Peter Sjöden, Rot 373</Key>
              <Key name="Postadress">79690 Älvdalen </Key>
              <Key name="Telefon">0251-10012</Key>
              <Key name="E-post"></Key>
              <Key name="Hemsida">[saknas] </Key>
              <Key name="Bankgiro">5782-8634</Key>
              <Key name="PlusGiro">440395-2</Key>
              <Key name="Organisationsnummer">652114-1181</Key>
              <Key name="Föreningenshemsidor"></Key>
            </Info>

    clubId
    Sport
    ExternalUrl
    Badge
    Founded
    IdrottOnlineId
    Address1
    Address2
    City
    PostalCode
    Phone
    Email
    VatNo
    BankGiro
    PlusGiro
    Presentation
    '''
    club_obj = createContent(portal_type='hejasverige.Club',
                             title=unicode(club.get('Name', None)),
                             VatNo=unicode(club.get('Organisationsnummer', None)),
                             Sport=unicode(club.get('Sport', None)),
                             Address1=unicode(club.get('Adress', None)),
                             PostalCode=unicode(club.get('Postadress', None)),
                             Phone=unicode(club.get('Telefon', None)),
                             Founded=unicode(club.get('Bildad', None)),
                             ExternalUrl=unicode(club.get('href', None)),
                             BankGiro=unicode(club.get('Bankgiro', None)),
                             PlusGiro=unicode(club.get('Plusgiro', None)),
                             Email=unicode(club.get('Epost', None)),
                             )


    # get image data if present
    if(club.get('ImagePath')):
        try:
            #import pdb; pdb.set_trace()
            imagepath = '/'.join([basepath, club.get('ImagePath')])
            filehandle = open(imagepath, 'r')

            imagedata = filehandle.read()
            imagename = club.get('href2')
            if not imagename:
                imagename = 'badge'

            contenttype = mimetypes.guess_type(imagepath)[0]

            value = NamedBlobFile(data=imagedata,
                                  contentType=contenttype,
                                  filename=unicode(imagename + imagepath[-4:])
                                  )

            fields = getFields(IClub)
            field = fields['Badge']
            field.set(field.interface(club_obj), value)
            #club_obj.Badge.set(content, value)

        except IOError, ex:
            print 'Unable to get image data.', str(ex)


    try:
        item = addContentToContainer(container=club.get('context'), object=club_obj, checkConstraints=False)
    except Exception, ex:
        print 'Problem when importing club', club_obj.title, 'due', str(ex)
        log(str(ex))
        import pdb; pdb.set_trace()
        raise
        #return None
    return item


def import_clubs_t(context, filename, destination_folder):
    import pdb; pdb.set_trace()
    print 'importing clubs...'

def import_clubs(context, filename, destination_folder):

    try:
       with open(filename): pass
    except IOError:
       print 'Oh dear. File %s does not exist' % filename
       #import pdb; pdb.set_trace()
    else:
        from zope.component.hooks import getSite
        site = getSite()
        districtfolder = getattr(site, destination_folder)
        # import pdb; pdb.set_trace()
        print 'Districtfolder length', len(districtfolder)

        basepath, tail = os.path.split(filename)
        print 'Base path:', basepath
        print 'Tail:', tail

        parser = etree.XMLParser(ns_clean=True)
        try:
            tree = etree.parse(filename, parser)

            root = tree.getroot()
            for district in root.getchildren():
                if district.tag == 'District':
                    districtid =  district.attrib.get('id')
                    districtname =  district.attrib.get('name')

                    new_district = try_add_district({'name': districtname, 'id': districtid, 'context': districtfolder})
                    #new_district = False

                    if new_district:
                        for council in district.getchildren()[0].getchildren():
                            if council.tag == 'Council':
                                councilid =  council.attrib.get('id')
                                councilname =  council.attrib.get('name')
                                
                                new_council = try_add_council({'name': councilname, 'id': councilid, 'context': new_district})
                                #new_council = True

                                if new_council:
                                    for club in council.getchildren()[0].getchildren():
                                        #import pdb; pdb.set_trace()
                                        new_club = {'context': new_council}
                                        for clubinfo in club.getchildren():
                                            if clubinfo.tag == 'Info':
                                                for info in clubinfo.getchildren():
                                                    #import pdb;pdb.set_trace()
                                                    if info.text:
                                                        new_club[info.get('name')] = info.text
                                            else:
                                                if clubinfo.text:
                                                    new_club[clubinfo.tag] = clubinfo.text
                                        try_add_club(new_club, basepath)
                            else:
                                print council.tag, 'ignored...'
                    transaction.savepoint()
                else:
                    print district.tag, 'ignored...'
        except Exception, ex:
            print "Exception occured:", ex

        print 'Ended... Now commit.'
        log('Committing...')
        transaction.commit()
        log('done')
        #pass
    # print etree.tostring(tree.getroot())
