"""Actual offline branching/replay tests for four-scene playable pilot."""
import copy,json,unittest
from tools.datingSimPilot import new_game,select,current,demo
from tools.hydraCastMediaBridge import STORY
class DatingSimPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.s=json.loads(STORY.read_text(encoding="utf-8"))
    def test_first_encounter_default_route(self):
        d=demo(self.s)
        self.assertEqual(d["ending"],"rehearsalEnd")
        self.assertEqual(d["steps"],2)
        self.assertEqual(d["affinity"],2)
        self.assertFalse(d["unrealBuilt"])
        self.assertFalse(d["providerCalled"])
    def test_alternative_route(self):
        start=new_game(self.s)
        state=select(self.s,start,1)
        self.assertEqual(current(self.s,state)["id"],"studio")
        end=select(self.s,state,0)
        self.assertEqual(end["nodeId"],"rehearsalEnd")
        self.assertEqual(end["affinity"],0)
    def test_state_is_immutable_copy(self):
        start=new_game(self.s);next_state=select(self.s,start,0)
        self.assertEqual(start["nodeId"],"arrival")
        self.assertEqual(start["affinity"],0)
        self.assertEqual(next_state["affinity"],1)
    def test_incorrect_choice_rejected(self):
        with self.assertRaisesRegex(ValueError,"CHOICE_RANGE"):select(self.s,new_game(self.s),10)
    def test_bool_choice_rejected(self):
        with self.assertRaisesRegex(ValueError,"CHOICE_TYPE"):select(self.s,new_game(self.s),True)
    def test_end_cannot_continue(self):
        state=new_game(self.s);state=select(self.s,state,0);state=select(self.s,state,0)
        with self.assertRaisesRegex(ValueError,"ALREADY_ENDING"):select(self.s,state,0)
    def test_affinity_clamps_at_ten(self):
        s=copy.deepcopy(self.s);s["nodes"][0]["choices"][0]["affinityDelta"]=2
        st=new_game(s);st["affinity"]=10
        self.assertEqual(select(s,st,0)["affinity"],10)
    def test_no_third_party_code_exec(self):
        s=copy.deepcopy(self.s);s["nodes"][0]["choices"][0]["next"]="__import__('os').system('true')"
        with self.assertRaisesRegex(ValueError,"INVALID_STORY"):new_game(s)
if __name__=="__main__":unittest.main()
