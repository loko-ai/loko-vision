from loguru import logger


class ModelCache:
    def __init__(self):
        self.model = None
        self.args = None
        self.hits = 0
        self.miss = 0

    def __call__(self, f):
        logger.debug("creating cache for methods")
        def tmp(dao, predictor_name, custom_model):
            logger.debug(self.args, self)
            # print(args, kwargs)
            if self.args and (predictor_name, custom_model) == self.args:
                self.hits += 1
                logger.debug(f"cache hit {predictor_name, custom_model}... hits{self.hits}, miss: {self.miss}")
                return self.model
            else:
                self.miss += 1
                logger.debug(f"cache miss {predictor_name, custom_model}...  hits{self.hits}, miss: {self.miss}")
                self.args = (predictor_name, custom_model)
                self.model = f(dao, predictor_name=predictor_name, custom_model=custom_model)
                return self.model

        return tmp
    #
    # def cache_info(self):
    #     return dict(miss=self.miss, )
