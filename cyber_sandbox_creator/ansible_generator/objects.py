from typing import Dict, Optional, List, Union


class Module:

    def __init__(self, name: str, attributes: Dict = {}):
        self.name: str = name
        self.attributes = attributes


class Task:

    def __init__(self, name: Optional[str], module: Module,
                 attributes: Dict = {}):
        self.name: Optional[str] = name
        self.module: Module = module
        self.attributes: Dict = attributes
        self.dictionary: Dict = {}

    def make_dict(self) -> Dict:
        """Make a dictionary for playbook generation"""
        task: Dict = {}
        if self.name:
            task["name"] = self.name
        if self.attributes:
            task.update(self.attributes)
        task[self.module.name] = self.module.attributes
        return task


class Play:

    def __init__(self, name: Optional[str], tasks: List[Task],
                 hosts: Optional[str] = None,
                 become: Optional[bool] = None,
                 attributes: Dict = {}):
        self.name: Optional[str] = name
        self.tasks: List[Task] = tasks
        self.hosts: Optional[str] = hosts
        self.become: Optional[bool] = become
        self.attributes: Dict = attributes

    def make_dict(self) -> Dict:
        """Make a dictionary for playbook generation"""
        play: Dict = {}
        if self.name:
            play["name"] = self.name
        if self.hosts is not None:
            play["hosts"] = str(self.hosts)
        if self.become:
            play["become"] = "yes"
        elif self.become is False:
            play["become"] = "no"
        play.update(self.attributes)
        tasks: List = []
        for task in self.tasks:
            tasks.append(task.make_dict())
        play["tasks"] = tasks
        return play


class Playbook:

    def __init__(self, plays: List[Play]):
        self.plays: List[Play] = plays

    def make_dict(self) -> Dict:
        """Make a dictionary for playbook generation"""
        plays: List = []
        for play in self.plays:
            plays.append(play.make_dict())
        return plays
