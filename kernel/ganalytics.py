from kernel.google import get_service

__author__ = 'Manuel Escriche'


class ga:
    def __init__(self, flags=None):
        service = get_service('analytics', flags=flags)
        accounts = service.management().accountSummaries().list().execute()
        self.views = []

        for account in accounts.get('items'):
            account_id = account.get('id')
            properties = service.management().webproperties().list(accountId=account_id).execute()

            for property in properties.get('items'):
                property_id = property.get('id')
                profiles = \
                    service.management().profiles().list(accountId=account_id, webPropertyId=property_id).execute()

                for profile in profiles.get('items'):
                    # profile_id = profile.get('id')
                    self.views.append({'account_id': account['id'],
                                       'account_name': account['name'],
                                       'property_id': property['id'],
                                       'property_name': property['name'],
                                       'website_url': property['websiteUrl'],
                                       'profile_id': profile['id'],
                                       'profile_name': profile['name']})

    def search_view(self, token):
        for view in self.views:
            if token in view['website_url']:
                return view
        else:
            return None
