from app.graph.builder import build_graph
from app.graph.state import AgentState


class TestGraphStructure:
    def test_graph_builds_without_error(self):
        graph = build_graph()
        assert graph is not None

    def test_graph_has_required_nodes(self):
        graph = build_graph()
        node_names = set(graph.nodes.keys())
        required = {"intake", "crisis_detector", "crisis_responder", "mood_checkin", "conversation", "tool_executor"}
        assert required.issubset(node_names), f"Missing nodes: {required - node_names}"

    def test_graph_compiles(self):
        graph = build_graph()
        compiled = graph.compile()
        assert compiled is not None
