# micropython doesn't have metaclasses or introspection
# so we need to do things annoyingly differently

class attrib:
	# single attribute
	def __init__(self, **kw):
		for k,v in kw.items():
			setattr(self,k,v)

class validators:
	@staticmethod
	def instance_of(exc):
		pass

attr = attrib
ib = attrib

class Factory:
	def __init__(self, f):
		self.f = f

def _init(self, **kw):
	seen = set()
	for k,v in kw.items():
		uk = '_'+k
		if k[0] != '_' and hasattr(self.__class__, uk):
			seen.add(uk)
			setattr(self,uk,v)
		else:
			setattr(self,k,v)

	for k in dir(self.__class__):
		if len(k)>1 and k[0] == '_' and k[1] == '_':
			continue
		if k in kw or k in seen:
			continue
		v = getattr(self.__class__,k)

		if isinstance(v,attrib):
			if hasattr(v,'factory'):
				v = v.factory()
			elif hasattr(v,'default_factory'):
				v = v.default_factory()
			else:
				v = v.default
				if isinstance(v,Factory):
					v = v.f()
			setattr(self,k,v)

def attrs(cls=None, **kw):
	def _attrs(cls):
		f = []
		for k in dir(cls):
			v = getattr(cls,k)
			if isinstance(v,attrib):
				f.append((k,v))

		cls._attrs = f
		if kw.get('init', True):
			cls.__init__ = _init
		return cls
		
	if cls is not None:
		return _attrs(cls)
	return _attrs

attributess = attrs
s = attrs
