


class GeoVistualiztion():

    def __init__(self, source):
        # the dictionary hosting all the data frames from the api server
        self.matrix = dict()

    def add_data_for_geovistualization(self,source):
        # Execute the source function and transform its return into a dataframe
        dataframe = pd.DataFrame(source())
        # save the dataframe into general matrix that stores every dataframe
        self.matrix[source.__name__] = dataframe
        return source