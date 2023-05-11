from ebaysdk.finding import Connection as Finding
from ebaysdk.shopping import Connection as Shopping
from ebaysdk.trading import Connection as Trading
from django.conf import settings
from browseapi import BrowseAPI

class EbayAPI:
    def __init__(self, token=settings.EBAY_TOKEN):
        self.api_find = Finding(domain='svcs.sandbox.ebay.com',
                                debug=True,
                                appid=settings.EBAY_APPID,
                                config_file=None)
        self.api_shop = Shopping(domain='api.ebay.com', 
                                 debug=True,
                                 appid=settings.EBAY_APPID,
                                 token=token, config_file=None)
        self.api_trade = Trading(domain='api.ebay.com',
                                 debug=True,
                                 appid=settings.EBAY_APPID,
                                 devid=settings.EBAY_DEVID,
                                 certid=settings.EBAY_CERID,
                                 token=token, config_file=None)
        self.api_browse = BrowseAPI(settings.EBAY_APPID, settings.EBAY_CERID)
        
        
    def refresh_token(user):
        api = Trading(domain='api.sandbox.ebay.com', debug=True, appid=settings.EBAY_APPID, devid=settings.EBAY_DEVID, certid=settings.EBAY_CERID, config_file=None)
        request = {
            'RequesterCredentials': {
                'eBayAuthToken': user.profile.refresh_token 
            }
        }
        try:
            response = api.execute('GetSessionID', request)
        except ConnectionError:
            raise
        user.profile.refresh_token = response.reply.eBayAuthToken
        user.save()
        return response.reply.eBayAuthToken

    def find(self, query):
        """
        # this is the old code for the Finding API
        request = {
            'keywords': query,
            'itemFilter': {
              'name': 'IncludeSelector',
              'value': 'ItemSpecifics'
            },
            'ListingType': 'All',
            'sortOrder': 'BestMatch'
        }
        response = self.api_find.execute('findItemsAdvanced', request)
        return response
        """
        if query == None:
            query = 'test'

        # new code for Browse API
        request = [{
            'q': query,
            'limit': 100,
        }]
        response = self.api_browse.execute('search', request)
        return response[0]
    
    def get_item(self, item_id):
        request = [{
            'item_id': item_id
        }]
        response = self.api_browse.execute('get_item', request)
        return response[0]

    def get_specs(self, item_id):
        request = {
            'ItemID': item_id,
            'DetailLevel': 'ItemReturnDescription',
            'IncludeItemSpecifics': True
        }
        #response = self.api_shop.execute('GetSingleItem', request)
        response = self.api_trade.execute('GetItem', request)
        return response