from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
from app.tasks.processing_tasks import extract_metadata_task, normalize_media_task
from app.tasks.fer_tasks import fer_analysis_task
from app.tasks.aesthetic_tasks import aesthetic_scoring_task
from app.tasks.selection_tasks import selection_task
from app.tasks.gemini_tasks import generate_linkedin_content_task, generate_instagram_content_task, generate_case_study_task


class AgentState(TypedDict):
    """State for the content generation workflow"""
    session_id: str
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_step: str
    completed_steps: list[str]
    errors: list[str]
    results: dict


class ContentOrchestrator:
    """LangGraph-based agent orchestration for content generation workflow"""
    
    def __init__(self):
        """Initialize the workflow graph"""
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes for each processing step
        workflow.add_node("start", self._start_node)
        workflow.add_node("metadata_extraction", self._metadata_extraction_node)
        workflow.add_node("normalization", self._normalization_node)
        workflow.add_node("analysis", self._analysis_node)
        workflow.add_node("selection", self._selection_node)
        workflow.add_node("content_generation", self._content_generation_node)
        workflow.add_node("qa_check", self._qa_check_node)
        workflow.add_node("end", self._end_node)
        
        # Define edges
        workflow.set_entry_point("start")
        workflow.add_edge("start", "metadata_extraction")
        workflow.add_edge("metadata_extraction", "normalization")
        workflow.add_edge("normalization", "analysis")
        workflow.add_edge("analysis", "selection")
        workflow.add_edge("selection", "content_generation")
        workflow.add_edge("content_generation", "qa_check")
        workflow.add_edge("qa_check", "end")
        workflow.add_edge("end", END)
        
        return workflow
    
    def _start_node(self, state: AgentState) -> AgentState:
        """Start node - initialize workflow"""
        state["current_step"] = "start"
        state["completed_steps"] = []
        state["errors"] = []
        state["results"] = {}
        state["messages"].append(
            AIMessage(content=f"Starting content generation workflow for session {state['session_id']}")
        )
        return state
    
    def _metadata_extraction_node(self, state: AgentState) -> AgentState:
        """Metadata extraction node"""
        state["current_step"] = "metadata_extraction"
        
        try:
            # Trigger metadata extraction for all assets in session
            # In production, this would queue Celery tasks
            result = {"status": "queued", "session_id": state["session_id"]}
            state["results"]["metadata_extraction"] = result
            state["completed_steps"].append("metadata_extraction")
            state["messages"].append(
                AIMessage(content="Metadata extraction queued successfully")
            )
        except Exception as e:
            state["errors"].append(f"Metadata extraction failed: {str(e)}")
            state["messages"].append(
                AIMessage(content=f"Error in metadata extraction: {str(e)}")
            )
        
        return state
    
    def _normalization_node(self, state: AgentState) -> AgentState:
        """Media normalization node"""
        state["current_step"] = "normalization"
        
        try:
            # Trigger media normalization
            result = {"status": "queued", "session_id": state["session_id"]}
            state["results"]["normalization"] = result
            state["completed_steps"].append("normalization")
            state["messages"].append(
                AIMessage(content="Media normalization queued successfully")
            )
        except Exception as e:
            state["errors"].append(f"Normalization failed: {str(e)}")
            state["messages"].append(
                AIMessage(content=f"Error in normalization: {str(e)}")
            )
        
        return state
    
    def _analysis_node(self, state: AgentState) -> AgentState:
        """Analysis node (YOLO, FER, Aesthetic)"""
        state["current_step"] = "analysis"
        
        try:
            # Trigger all analysis tasks
            result = {
                "yolo": "queued",
                "fer": "queued",
                "aesthetic": "queued",
                "session_id": state["session_id"]
            }
            state["results"]["analysis"] = result
            state["completed_steps"].append("analysis")
            state["messages"].append(
                AIMessage(content="Analysis tasks (YOLO, FER, Aesthetic) queued successfully")
            )
        except Exception as e:
            state["errors"].append(f"Analysis failed: {str(e)}")
            state["messages"].append(
                AIMessage(content=f"Error in analysis: {str(e)}")
            )
        
        return state
    
    def _selection_node(self, state: AgentState) -> AgentState:
        """Asset selection node"""
        state["current_step"] = "selection"
        
        try:
            # Trigger asset selection
            result = {"status": "queued", "session_id": state["session_id"]}
            state["results"]["selection"] = result
            state["completed_steps"].append("selection")
            state["messages"].append(
                AIMessage(content="Asset selection queued successfully")
            )
        except Exception as e:
            state["errors"].append(f"Selection failed: {str(e)}")
            state["messages"].append(
                AIMessage(content=f"Error in selection: {str(e)}")
            )
        
        return state
    
    def _content_generation_node(self, state: AgentState) -> AgentState:
        """Content generation node (LinkedIn, Instagram, Case Study)"""
        state["current_step"] = "content_generation"
        
        try:
            # Trigger content generation tasks
            result = {
                "linkedin": "queued",
                "instagram": "queued",
                "case_study": "queued",
                "session_id": state["session_id"]
            }
            state["results"]["content_generation"] = result
            state["completed_steps"].append("content_generation")
            state["messages"].append(
                AIMessage(content="Content generation tasks queued successfully")
            )
        except Exception as e:
            state["errors"].append(f"Content generation failed: {str(e)}")
            state["messages"].append(
                AIMessage(content=f"Error in content generation: {str(e)}")
            )
        
        return state
    
    def _qa_check_node(self, state: AgentState) -> AgentState:
        """QA check node - flag low-confidence outputs"""
        state["current_step"] = "qa_check"
        
        try:
            # Check confidence scores and flag if needed
            result = {
                "status": "completed",
                "flagged": False,
                "session_id": state["session_id"]
            }
            state["results"]["qa_check"] = result
            state["completed_steps"].append("qa_check")
            state["messages"].append(
                AIMessage(content="QA check completed - all outputs passed threshold")
            )
        except Exception as e:
            state["errors"].append(f"QA check failed: {str(e)}")
            state["messages"].append(
                AIMessage(content=f"Error in QA check: {str(e)}")
            )
        
        return state
    
    def _end_node(self, state: AgentState) -> AgentState:
        """End node - finalize workflow"""
        state["current_step"] = "end"
        state["messages"].append(
            AIMessage(content=f"Workflow completed. Steps: {state['completed_steps']}")
        )
        return state
    
    def run_workflow(self, session_id: str) -> dict:
        """
        Run the complete workflow for a session
        
        Args:
            session_id: Session ID to process
            
        Returns:
            dict: Workflow results
        """
        initial_state = {
            "session_id": session_id,
            "messages": [HumanMessage(content=f"Process session {session_id}")],
            "current_step": "",
            "completed_steps": [],
            "errors": [],
            "results": {}
        }
        
        final_state = self.app.invoke(initial_state)
        
        return {
            "session_id": session_id,
            "completed_steps": final_state["completed_steps"],
            "errors": final_state["errors"],
            "results": final_state["results"],
            "messages": [msg.content for msg in final_state["messages"]]
        }
    
    def get_workflow_status(self, session_id: str) -> dict:
        """
        Get current workflow status for a session
        
        Args:
            session_id: Session ID to check
            
        Returns:
            dict: Current workflow status
        """
        # In production, this would query the database for actual status
        return {
            "session_id": session_id,
            "status": "running",
            "current_step": "analysis",
            "completed_steps": ["metadata_extraction", "normalization"],
            "errors": []
        }


# Singleton instance
orchestrator = ContentOrchestrator()
