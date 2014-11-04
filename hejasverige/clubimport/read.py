# -*- coding: utf-8 -*-

import logging
import os
import mimetypes
import datetime
from lxml import etree

import transaction

from zope.component import getUtility
from zope.component.hooks import getSite
from zope.schema import getFields

from z3c.relationfield.relation import RelationValue

from plone.dexterity.utils import createContent, addContentToContainer
from plone.namedfile.file import NamedBlobFile

from plone.namedfile.interfaces import INamedFileField, INamedImageField
from hejasverige.content.sports.interfaces import IClub
from zope.intid.interfaces import IIntIds

from Products.CMFPlone.utils import safe_unicode

import plone.api


logger = logging.getLogger(__name__)


def parse_date(s, fmt='%Y-%m-%d'):
    if s:
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except Exception as e:
            pass


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


def query_object(context, portal_type, **kwargs):
    site = getSite()
    params = dict(portal_type=portal_type, **kwargs)
    if context is not None:
        params['path'] = dict(query='/'.join(context.getPhysicalPath()))
    q = site.portal_catalog(params)
    b = next(iter(q), None)
    if b:
        return b.getObject()


def get_or_create_district(context, title, id_):
    ob = query_object(context, 'hejasverige.District', Title=title)
    if ob is None:
        ob = plone.api.content.create(context, 'hejasverige.District',
            title=safe_unicode(title), district_id=safe_unicode(id_))
        logger.info('Added district %s %s', title, ob.absolute_url())
    else:
        logger.info('Found district %s %s', title, ob.absolute_url())
    return ob


def get_or_create_council(context, title, id_):
    ob = query_object(context, 'hejasverige.Council', Title=title)
    if ob is None:
        ob = plone.api.content.create(context, 'hejasverige.Council',
            title=safe_unicode(title), council_id=safe_unicode(id_))
        logger.info('Added council %s %s', title, ob.absolute_url())
    else:
        logger.info('Found council %s %s', title, ob.absolute_url())
    return ob


def get_or_create_sport(context, title):
    ob = query_object(context, 'hejasverige.Sport', Title=title)
    if ob is None:
        ob = plone.api.content.create(context, 'hejasverige.Sport',
                                      title=safe_unicode(title))
        logger.info('Added sport %s %s', title, ob.absolute_url())
    else:
        logger.info('Found sport %s %s', title, ob.absolute_url())
    return ob


def try_add_club(context, club_data, basepath):
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

    ob = query_object(context, 'hejasverige.Club', Title=club_data['Name'])
    if ob is not None:
        logger.info('Found club %s %s', club_data['Name'], ob.absolute_url())
        return ob

    sport_title = club_data.get('Sport')
    if not sport_title:
        logger.info('Missing sport %r', club_data)
        return
    sport_folder = query_object(None, 'hejasverige.SportFolder')
    sport_ob = get_or_create_sport(sport_folder, sport_title)
    sport_id = getUtility(IIntIds).getId(sport_ob)
    sport_rel = RelationValue(sport_id)

    ob = plone.api.content.create(context, 'hejasverige.Club',
        title=unicode(club_data['Name']),
        vat_no=unicode(club_data.get('Organisationsnummer', None)),
        sport=sport_rel,
        address1=unicode(club_data.get('Adress', None)),
        postal_code=unicode(club_data.get('Postadress', None)),
        phone=unicode(club_data.get('Telefon', None)),
        founded=parse_date(club_data.get('Bildad', None)),
        external_url=unicode(club_data.get('href', None)),
        bank_giro=unicode(club_data.get('Bankgiro', None)),
        plus_giro=unicode(club_data.get('Plusgiro', None)),
        email=unicode(club_data.get('Epost', None)),
    )

    logger.info('Added club %s %s', club_data['Name'], ob.absolute_url())

    # get image data if present
    if(club_data.get('ImagePath')):
        try:
            #import pdb; pdb.set_trace()
            imagepath = '/'.join([basepath, club_data.get('ImagePath')])
            imagedata = open(imagepath, 'r').read()
            imagename = club_data.get('href2')
            if not imagename:
                imagename = 'badge'
            contenttype = mimetypes.guess_type(imagepath)[0]
            value = NamedBlobFile(data=imagedata,
                contentType=contenttype, filename=unicode(imagename + imagepath[-4:]))
            fields = getFields(IClub)
            fields['badge'].set(fields['badge'].interface(ob), value)
        except IOError, ex:
            logger.error('Unable to get image data for club %s.', club_data['Name'])

    return ob


def import_clubs(context, filename):

    site = getSite()
    basepath, tail = os.path.split(filename)
    districtfolder = query_object(site, 'hejasverige.DistrictFolder')

    parser = etree.XMLParser(ns_clean=True)
    root = etree.parse(filename, parser).getroot()
    count = 0
    for district in root.getchildren():
        if district.tag == 'District':
            district_ob = get_or_create_district(districtfolder,
                district.attrib['name'], district.attrib['id'])
            for council in district.getchildren()[0].getchildren():
                if council.tag == 'Council':
                    council_ob = get_or_create_council(district_ob,
                        council.attrib['name'], council.attrib['id'])
                    for i, club in enumerate(council.getchildren()[0].getchildren()):
                        if i > 10: break # XXX: only 10 clubs per council
                        club_data = {}
                        for clubinfo in club.getchildren():
                            if clubinfo.tag == 'Info':
                                for info in clubinfo.getchildren():
                                    if info.text:
                                        club_data[info.get('name')] = info.text
                            else:
                                if clubinfo.text:
                                    club_data[clubinfo.tag] = clubinfo.text
                        logger.info('--- %s %r', club_data['Name'], club_data)
                        sp = transaction.savepoint()
                        try:
                            try_add_club(council_ob, club_data, basepath)
                        except Exception as e:
                            logger.exception(e)
                            sp.rollback()
                        count += 1
    logger.info('Committing...')
    transaction.commit()
    logger.info('done')
