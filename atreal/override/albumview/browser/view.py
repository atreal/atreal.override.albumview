from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.interface.interfaces import IInterface

from zope.component import getMultiAdapter, queryUtility, getUtility
from atreal.filecart.browser.controlpanel import IFileCartSchema
from Products.CMFPlone.interfaces import IPloneSiteRoot

from Products.CMFPlone.utils import base_hasattr

from atreal.filecart import FileCartMessageFactory as _

class FolderCartView (BrowserView) :
    """
    """

    @property
    def _options (self):
        _siteroot = queryUtility (IPloneSiteRoot)
        return IFileCartSchema (_siteroot)
    
    def test (self, a, b, c):
        if a:
            return b
        else:
            return c

    def isFileCartInstalled(self):
        """ 
        """
        if queryUtility(IInterface, name=u'atreal.filecart.interfaces.IFileCartSite', default=False):
            return True
        return False

    def canUseFileCart(self):
        """ 
        """
        # Use portal_membership tool for checking permissions
        mtool = self.context.portal_membership
        checkPermission = mtool.checkPermission
        # checkPermissions returns true if permission is granted
        if checkPermission('atreal.filecart: Use Cart', self.context):
            return True
        return False
    
    def contents (self, **kwargs):
        """
        """
        search = False
        if kwargs.has_key('search'):
            if kwargs['search']:
                search = True
                if kwargs['REQUEST'].has_key('SearchableText'):
                    if '*' not in kwargs['REQUEST'].get('SearchableText'):
                        kwargs['REQUEST'].set('SearchableText', kwargs['REQUEST'].get('SearchableText')+'*')
        
        if search :
            queryMethod = self.context.queryCatalog
            brains = queryMethod(REQUEST=kwargs['REQUEST'],
                                 use_types_blacklist=kwargs['use_types_blacklist'],
                                 use_navigation_root=kwargs['use_navigation_root'])
        else:
            if self.context.portal_type == 'Topic':
                queryMethod = self.context.queryCatalog
            else:
                queryMethod = self.context.getFolderContents
            searchContentTypes = self.context.plone_utils.getUserFriendlyTypes()
            brains = queryMethod({'portal_type':searchContentTypes})
        
        
        brains_image = queryMethod({'object_provides':'atreal.richfile.image.interfaces.IImage'})
        
        brains_image_uid = []
        for brain_image in brains_image:
            brains_image_uid.append(brain_image.UID)

        if self.isFileCartInstalled() and self.canUseFileCart():
            brains_cartable = queryMethod({'object_provides':'atreal.filecart.interfaces.IFileCartable'})
            
            brains_cartable_uid = []
            for brain_cartable in brains_cartable:
                brains_cartable_uid.append(brain_cartable.UID)
        
        self.infos = {}
        
        for brain in brains:
            # Thumbs
            if brain.portal_type == "Image":
                thumb = brain.getURL()+'/image_thumb'
            elif brain.UID in brains_image_uid:
                thumb = brain.getURL()+'/rfimage/thumb'
            else:
                thumb = self.context.portal_url()+'/rf_'+brain.getIcon
            
            # Cartable
            cartable = False
            if self.isFileCartInstalled() and self.canUseFileCart():
                if brain.UID in brains_cartable_uid:
                    cartable = True
            
            #
            self.infos[brain.UID] = dict({
                'thumb': thumb,
                'cartable': cartable})
        
        return brains
