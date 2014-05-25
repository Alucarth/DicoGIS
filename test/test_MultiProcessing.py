import multiprocessing as mp

class Foo():
    @staticmethod
    def work(self):
        pass

pool = mp.Pool()
foo = Foo()
pool.apply_async(foo.work)
pool.close()
pool.join()