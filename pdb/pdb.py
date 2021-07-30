class Pdb:
    def reset(self):
        pass

    def set_trace(self):
        raise NotImplementedError("Pdb.set_trace")


def set_trace():
    raise NotImplementedError("set_trace")
