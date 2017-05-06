from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        
        json_data = {
            "name": ddd,
            "birth_year": ddd,
            
        }
        setattr("name", json_data["name"])
        """
        for key in json_data:
            setattr(self, key, json_data[key])

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        
        if our subclass is People:
            return api_client.get_people(resource_id)
            
        if the subclass is Films:
            return api_client.get_films(resource_id)
        
        getattr(object, name)
        name is a string
        object."name"
        """
        method_name = "get_" + cls.RESOURCE_NAME
        actual_method = getattr(api_client, method_name)
        return cls(actual_method(resource_id))

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        
        depending on whether we're in People or Films, we want to return
        an instance of PeopleQuerySet or FilmsQuerySet
        --need to turn the string "PeopleQuerySet" into a callable
        """
        class_name = cls.RESOURCE_NAME.title() + "QuerySet"
        return eval(class_name)()


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self.results = []
        self.current_result = 0
        self.current_page = 0
        
    def __iter__(self):
        return self
    
    @classmethod
    def _get_results_page(cls, page_number):
        method_name = "get_" + cls.RESOURCE_NAME
        actual_method = getattr(api_client, method_name)
        json_data = actual_method(**{'page':page_number})
        return json_data
            
    
    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        if self.current_result >= len(self.results):
            # not enough results, so get a new page of results
            try:
                new_results = self._get_results_page(self.current_page + 1)["results"]
            except SWAPIClientError:
                raise StopIteration
            self.current_page += 1
            self.results += new_results
        the_result = self.results[self.current_result]
        self.current_result += 1
        
        return eval(self.RESOURCE_NAME.title())(the_result)

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return self._get_results_page(1)["count"]


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
