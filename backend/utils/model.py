# Kind of abstract class as template for the different models

class Model:
    def __init__(self, name, load_function):
        self.model_name = name
        self.load_function = load_function
        self.model = None

    def get_name(self):
        return self.model_name

    def load_model(self):
        self.model = self.load_function(self.model_name)
        return self.model

    def get_vector(self, term):
        if self.model_name in ["w2v", "glove", "fasttext"]:
            vec = self.model.get_vector(term)
            return vec
        elif self.model_name == "infersent":
            vec = self.model.encode([term])
            return vec
        elif self.model_name == "use":
            vec = self.model([term])
            return vec


class ModelHandler:
    def __init__(self, models):
        self.models = models
        self.last_loaded_model = None

    def load_model(self, model_name):
        if self.last_loaded_model != model_name:
            self.models[model_name].load_model()
            self.last_loaded_model = model_name
        return True

    def get(self, model_name):
        print("Return model {}".format(model_name))
        return self.models[model_name]

    def add(self, model):
        if type(model) == Model:
            self.models[model.get_name()] = model
            return True
        return False
