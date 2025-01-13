# rodos-middleware: This file is a part of the Master Thesis of Sebastian Kind 2023




localTopics = []

class Topic():
#    handlers = []
    #    gwHandlers = []

    def __init__(self, topicId):
        self.handlers = []
        self.gwHandlers = []
        self.topicId = topicId
        localTopics.append(self)
        pass

    def __repr__(self):
        return repr("id = {}".format(self.topicId))

    def publish(self, data):
        for h in self.handlers:
            # print(self.handlers)
            # print("publish: calling handlers")
            h(data)
        for h in self.gwHandlers:
            # print(self.handlers)
            # print("publish: calling gwhandlers")
            h(data, self.topicId)



    def addSubscriber(self, handler):
        self.handlers.append(handler)
        #print("self.topicId", self.topicId, self.handlers)


    def publishFromGateway(self, data): # dont broadcast over gateway over and over again
        for h in self.handlers:
            # print("publish: calling handlers")
            h(data)
