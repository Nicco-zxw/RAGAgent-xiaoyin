import unittest
from enterprise_qa.core import Agent, MockModel, Tools

class Acceptance(unittest.TestCase):
    def run_case(self, data='data/clear.json', question='报销期限多久？', **kw):
        history = kw.pop('history', None)
        return Agent(MockModel(), Tools(data, kw.pop('fail_first', None)), **kw).run(question, history)
    def test_clear(self):
        r = self.run_case()
        self.assertEqual(r['status'], 'answered')
        self.assertIn('30', r['answer'])
    def test_conflict(self):
        r = self.run_case('data/conflict.json')
        self.assertEqual(r['status'], 'needs_clarification')
        self.assertEqual(len(r['citations']), 2)
    def test_outside(self):
        self.assertEqual(self.run_case(question='明天天气怎样')['status'], 'insufficient_evidence')
    def test_paraphrase(self):
        self.assertEqual(self.run_case(question='费用最晚什么时候交')['status'], 'answered')
    def test_context(self):
        r = self.run_case(question='那试用期员工呢？', history=[{'role':'user','content':'报销期限多久'}])
        self.assertEqual(r['status'], 'insufficient_evidence')
    def test_failure(self):
        self.assertEqual(self.run_case(fail_first='read_passage')['status'], 'answered')
    def test_budget(self):
        self.assertEqual(self.run_case(max_steps=1)['status'], 'budget_exceeded')
    def test_mutation(self):
        self.assertIn('45', self.run_case('data/changed.json')['answer'])
    def test_fake_citation(self):
        class Bad:
            def choose(self, state):
                return {'action':'finish','arguments':{'status':'answered','answer':'假的','citations':[{'document_id':'X','passage_id':'Y','quote':'假'}]}}
        r = Agent(Bad(), Tools('data/clear.json'), max_steps=2).run('报销')
        self.assertEqual(r['status'], 'budget_exceeded')

if __name__ == '__main__': unittest.main()

