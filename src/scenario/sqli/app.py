from parser import GenerateVulnSQLInjectionEndpoint

from .schema import Base

app = GenerateVulnSQLInjectionEndpoint(
  __name__, 'sqlite+aiosqlite:///db/main.db', 'sqlite+aiosqlite:///db/fake.db', Base, 'sqlite'
)


__all__ = ['app']
