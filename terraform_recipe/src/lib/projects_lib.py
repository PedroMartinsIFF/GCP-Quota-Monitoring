import functools

import cachetools

from lib import gcp

class Project:
    """Object to represent project data."""
    def __init__(self):
        self.id = ''  
        self.name = ''
        self.number = ''
        self.parent_type = ''
        self.parent_id = ''
        self.parent_name = ''
        self.ancestry = ''
        self.timestamp = ''

    def to_dict(self):
        """Return objects data as dict."""
        return {
            'id': self.id,
            'name': self.name,
            'number': self.number,
            'parent_type': self.parent_type,
            'parent_id': self.parent_id,
            'parent_name': self.parent_name,
            'ancestry': self.ancestry,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        """Build Project object from dict data."""
        prj = cls()
        prj.id = data.get('id', '')
        prj.name = data.get('name', '')
        prj.number = data.get('number', '')
        prj.parent_type = data.get('parent_type', '')
        prj.parent_id = data.get('parent_id', '')
        prj.parent_name = data.get('parent_name', '')
        prj.ancestry = data.get('ancestry', '')
        prj.timestamp = data.get('timestamp', '')
        return prj

    def __str__(self):
        return 'Project - Id: %s, Name: %s' % (self.id, self.name)

def _project_data(project_id, prjs_client=None, creds=None):
    """Query and get active project."""
    prjs_client = prjs_client or gcp.projects_service(creds=creds)
    request = prjs_client.get(projectId=project_id)
    return gcp.execute_request(request)

