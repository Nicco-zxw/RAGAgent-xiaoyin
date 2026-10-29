import json
import unittest
from enterprise_qa.core import Agent, MockModel, Tools

class Sequence:
    def __init__(self, values): self.values = iter(values)
    def choose(self, state):
        value = next(self.values)
        if isinstance(value, Exception): raise value
        return value

def stop():
    return {'action':'finish','arguments':{'status':'insufficient_evidence','answer':'资料不足','citations':[],'gaps':['缺少资料'],'conflicts':[]}}

class Robustness(unittest.TestCase):
    def test_bad_shapes_can_recover(self):
        for bad in [None, [], 'bad', {'action':'search_documents','arguments':None}, {'action':'finish','arguments':{'citations':None}}, {'action':'finish','arguments':{'status':[]}}]:
            with self.subTest(bad=bad):
                r=Agent(Sequence([bad,stop()]),Tools('data/clear.json'),max_steps=2).run('问题')
                self.assertEqual(r['status'],'insufficient_evidence')
    def test_invalid_json_can_recover(self):
        r=Agent(Sequence([json.JSONDecodeError('bad','x',0),stop()]),Tools('data/clear.json'),max_steps=2).run('问题')
        self.assertEqual(r['status'],'insufficient_evidence')
    def test_persistent_failure(self):
        class Broken(Tools):
            def execute(self, name, args): return {'ok':False,'data':None,'error':'TIMEOUT'}
        self.assertEqual(Agent(MockModel(),Broken('data/clear.json')).run('报销')['status'],'tool_error')
    def test_conflict_is_structured(self):
        r=Agent(MockModel(),Tools('data/conflict.json')).run('报销')
        self.assertTrue(r['conflicts'])
        self.assertFalse(r['conflicts'][0]['resolved'])
    def test_tool_argument_validation(self):
        t=Tools('data/clear.json')
        for args in [None, [], {'query':''}, {'query':'报销','top_k':True}, {'query':'报销','top_k':'five'}]:
            self.assertFalse(t.execute('search_documents',args)['ok'])
