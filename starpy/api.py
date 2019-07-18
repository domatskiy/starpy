import requests
import pandas as pd


class StarPyMae(object):

    """
    Main Class \n
    Description: Makes the api call for data manipulation. \n
    """

    # Endpoints

    _VEHICLES = 'vehicles'
    _PEOPLE = 'people'
    _STAR_SHIPS = 'starships'

    # Main methods

    def __init__(self):
        self._base_url = 'https://swapi.co/api'

    def _sget(self, endpoint, resource=None):
        """ Get request to _base_url
        :param endpoint, resource, :type str, int
        """
        if resource is None:
            end, r = '%s/%s', (self._base_url, endpoint)
        else:
            end, r = '%s/%s/%s/', (self._base_url, endpoint, resource)
        re = requests.get(end % r)
        if re.status_code == 200:
            re = re.json()
        else:
            raise Exception('Not found or invalid request. Try again with a different one!')

        return re

    def _get_next_page(self, endpoint, i):
        """ Gets new/next page for manipulation """
        return self._sget(endpoint='%s?page=%s' % (endpoint, i), resource=None)


class GetStars(StarPyMae):
    """ Inherits methods and variables from StarPyMae Class"""

    def _get_people(self, res=None):
        """ Gets the first page of people's endpoint if the parameter res is passed as None \n
            otherwise it returns data from a specific person's id.
        """
        return self._sget(self._PEOPLE, res)

    def get_person_by_id(self, rid):
        """ Gets data from person's id passed as argument \n
        :param rid :type int
        """
        return self._get_people(rid)

    def _get_transport(self, transport, res=None):
        """ Send a get request passing type of transport and resource as arguments"""
        return self._sget(transport, res)

    def _get_vehicles(self, res=None):
        """ Gets vehicles data from first page if parameter res receives None \n
            otherwise it gets vehicles data of specific vehicle """
        return self._get_transport(self._VEHICLES, res)

    def get_vehicles_by_id(self, rid):
        """ Gets vehicles data from its id passed as argument to rid parameter \n
        :param rid :type int
        """
        return self._get_vehicles(rid)

    def _get_starships(self, res=None):
        """ Gets star ships data from first page if parameter res receives None \n
            otherwise it gets star ships data of specific star ship """
        return self._get_transport(self._STAR_SHIPS, res)

    def get_starships_by_id(self, rid):
        """ Gets star ship from id passed as argument to the rid parameter \n
        :param rid :type: int
        :return:
        """
        return self._get_starships(rid)

    def _if_transport(self, transport):
        """ It checks which kind of transport is passed as argument to the next methods\n
            and returns data from first page of it.
        :param transport :type str \n
        :return dict
        """
        v = None
        if transport == self._VEHICLES:
            v = self._get_vehicles()
        if transport == self._STAR_SHIPS:
            v = self._get_starships()
        if v is None:
            raise Exception('Choose between self._VEHICLES or self._STAR_SHIPS')
        return v

    def _find_pilots_to_list(self, transport):
        """ Find pilots and append to a list depending on type of transport passed as argument \n
        :param transport :type str \n
        :return list
        """
        v = self._if_transport(transport)
        page, li2 = 1, []
        while v['next'] is not None:
            v = v['results']
            for i in self.l(v):
                if v[i]['pilots'] and v[i]['max_atmosphering_speed']:
                    lista = v[i]['pilots'], v[i]['name'], v[i]['max_atmosphering_speed']
                    li2.append(lista)
            page += 1
            v = self._get_next_page(transport, page)

        v = self._get_next_page(transport, page)['results']
        for j in self.l(v):
            if v[j]['pilots'] and v[j]['max_atmosphering_speed']:
                lista = v[j]['pilots'], v[j]['name'], v[j]['max_atmosphering_speed']
                li2.append(lista)
        return li2

    def find_pilots_from_v(self):
        """ Finds vehicle pilots """
        return self._find_pilots_to_list(self._VEHICLES)

    def find_pilots_from_s(self):
        """ Finds star ship pilots """
        return self._find_pilots_to_list(self._STAR_SHIPS)

    def _find_fastest_transport_name_and_its_speed(self, transport):
        """ Finds the fastest transport name and its speed \n
        :param transport :type str \n
        :return list, dict
        """
        df = self._df_of_transport(transport)
        f, kl = df[2].nlargest(3), []
        for i in self.l(f):
            n_index = f.index[i]
            n_transporte = df[1][n_index]
            kl.append(n_transporte)
        return kl, f.to_dict()

    def _find_fastest_speed(self, transport):
        """ Finds fastest transport and returns its speed depending on the parameter passed. \n
            Ex: self._VEHICLES or self.STAR_SHIPS \n
        :param transport :type str
        """
        return self._find_fastest_transport_name_and_its_speed(transport)[1]

    def _find_fastest_trans_name(self, transport):
        """ Finds fastest transport and returns its name depending on the parameter passed. \n
            Ex: self._VEHICLES or self.STAR_SHIPS \n
        :param transport :type str
        """
        return self._find_fastest_transport_name_and_its_speed(transport)[0]

    def find_fastest_v(self):
        """ Finds the fastest vehicles with at least one pilot associated to it """
        return self._find_fastest_speed(self._VEHICLES)

    def find_fastest_s(self):
        """ Finds the fastest star ships with at least one pilot associated to it """
        return self._find_fastest_speed(self._STAR_SHIPS)

    def _df_of_transport(self, transport):
        """ Creates pandas DataFrame to easier data manipulation. \n
        :param transport :type str \n
        :return df :type pandas DataFrame
         """
        l2 = self._find_pilots_to_list(transport)
        df = pd.DataFrame(l2)
        df[2].replace(regex=True, inplace=True, to_replace='\D', value=r'0')
        df[2] = pd.to_numeric(df[2])
        return df

    def _url_of_fastest_pilot(self, transport):
        """ Returns url's list of fastest pilots depending on parameter. \n
            Ex:  ['https://swapi.co/api/people/35/', 'https://swapi.co/api/people/10/'] \n
        :param transport :type str \n
        :return df :type list
        """
        fastest = self._find_fastest_speed(transport)
        fastest, url_list = list(fastest.keys()), []
        df = self._df_of_transport(transport)
        for i in self.l(fastest):
            n = fastest[i]
            url_list.append(df[0][n][0])
        return url_list

    def _url_fastest_pilots_v(self):
        """ Returns url's list of fastest pilots driving Vehicles. """
        return self._url_of_fastest_pilot(self._VEHICLES)

    def _url_fastest_pilot_v(self):
        """ Returns urls of fastest pilot driving Vehicles. """
        return self._url_of_fastest_pilot(self._VEHICLES)[0]

    def _url_fastest_pilots_s(self):
        """ Returns url's list of fastest pilots driving StarShips. """
        return self._url_of_fastest_pilot(self._STAR_SHIPS)

    def _url_fastest_pilot_s(self):
        """ Returns urls of fastest pilot driving StarShips. """
        return self._url_of_fastest_pilot(self._STAR_SHIPS)[0]

    def _id_fastest_pilots(self, transport):
        """ Returns id's list of fastest pilots according to the parameter passed \n
        :param transport :type str \n
        :return list
        """
        pilot_id, il = self._url_of_fastest_pilot(transport), []
        for i in self.l(pilot_id):
            pid = pilot_id[i].split('/')[-2]
            il.append(pid)
        return il

    def id_fastest_pilots_v(self):
        """ Returns id's list of fastest pilots driving Vehicles. """
        return self._id_fastest_pilots(self._VEHICLES)

    def id_fastest_pilot_v(self):
        """ Returns id of fastest pilot driving Vehicles. """
        return self._id_fastest_pilots(self._VEHICLES)[0]

    def id_fastest_pilots_s(self):
        """ Returns id's list of fastest pilots driving StarShips. """
        return self._id_fastest_pilots(self._STAR_SHIPS)

    def id_fastest_pilot_s(self):
        """ Returns id of fastest pilot driving StarShips. """
        return self._id_fastest_pilots(self._STAR_SHIPS)[0]

    def _pilot_names(self, transport):
        """ Gets the fastest pilot names depending on the parameter \n
        :param transport :type str \n
        :return list
        """
        l_ids, l_names = self._id_fastest_pilots(transport), []
        for i in self.l(l_ids):
            name = self.get_person_by_id(int(l_ids[i]))['name']
            l_names.append(name)
        return l_names

    def pilot_names_v(self):
        """ Returns the fastest pilot names driving Vehicles """
        return self._pilot_names(self._VEHICLES)

    def pilot_names_s(self):
        """ Returns the fastest pilot names driving StarShips """
        return self._pilot_names(self._STAR_SHIPS)

    def _name_and_max_speed(self, transport):
        """ Returns pilots name and max. speed according to the parameter passed \n
        :param transport :type str \n
        :return list
        """
        n, sp, lis = self._pilot_names(transport), list(self._find_fastest_speed(transport).values()), []
        trans = self._find_fastest_trans_name(transport)
        transport_name = transport.capitalize()[:-1] + ' name'
        for i in self.l(n):
            li = [{'Name': n[i], 'Max. Speed': sp[i], transport_name: trans[i]}]
            lis.append(li)
        return lis

    def name_and_max_speed_v(self):
        """ Returns pilots name and its Vehicles max. speed"""
        return self._name_and_max_speed(self._VEHICLES)

    def name_and_max_speed_s(self):
        """ Returns pilots name and its StarShips max. speed"""
        return self._name_and_max_speed(self._STAR_SHIPS)

    def _by_idpeople_return_transport_speed(self, transport, idname):
        """ Returns transport speed by passing type of transport and id of person \n
        :param transport, idname \n
        :type str, int \n
        :return list
         """
        lss, transport_urls_id = [], self.get_person_by_id(idname)[transport]
        for i in self.l(transport_urls_id):
            url_id = transport_urls_id[i].split('/')[-2]
            speed = self._by_idtransports_return_its_speed(transport, url_id)
            l_data = [{'transport_id': url_id, 'Max. Speed': speed}]
            lss.append(l_data)
        return lss

    def _by_idtransports_return_its_speed(self, transport, idtrans):
        """ Returns transport speed by passing type of transport and its id as an argument """
        return self._get_transport(transport, idtrans)['max_atmosphering_speed']

    def starships_speed_by_person(self, idpeople):
        """ Returns StarShips speed by passing person's id as an argument """
        return self._by_idpeople_return_transport_speed(self._STAR_SHIPS, idpeople)

    def vehicles_speed_by_person(self, idpeople):
        """ Returns Vehicles speed by passing person's id as an argument """
        return self._by_idpeople_return_transport_speed(self._VEHICLES, idpeople)

    def _fastest_person(self, transport):
        """ Returns fastest person's name, its transport's name, and its max. \n
            speed reached according to the type of transport passed as an argument"""
        return self._name_and_max_speed(transport)[0]

    def fastest_person_with_v(self):
        """ Returns fastest person's name, its transport's name and its max. \n
            speed reached driving Vehicles """
        return self._fastest_person(self._VEHICLES)

    def fastest_person_with_s(self):
        """ Returns fastest person's name, its transport's name and its max. \n
            speed reached driving StarShips """
        return self._fastest_person(self._STAR_SHIPS)

    def l(self, data):
        """ Auxiliary method """
        return range(len(data))


if __name__ == '__main__':
    s = GetStars()
    print('\n===== Lets begin the search ===== '
          '\n StarPy | Star Wars with Python'
          '\n=================================')