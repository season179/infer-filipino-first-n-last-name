from pydantic import BaseModel, Field
from typing import List, Any, Union

class ParsedNameResult(BaseModel):
    first_name: str | None = Field(default=None, description="Identified first name(s).")
    last_name: str | None = Field(default=None, description="Identified last name(s).")
    parsing_method: str = Field(default="Unknown", description="Primary logic used by LLM.")
    original_name: str = Field(..., description="Original input name string.")
    error_message: str | None = Field(default=None, description="Error message if parsing failed for this specific name.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "ParsedFirstName": self.first_name,
            "ParsedLastName": self.last_name,
            "ParsingMethod": self.parsing_method,
            "OriginalName": self.original_name,
            "ErrorMessage": self.error_message
        }

class BatchParseResponse(BaseModel):
    results: List[ParsedNameResult] = Field(..., description="A list containing a parse result for each name in the input batch.")

class FailedBatch(BaseModel):
    batch_input_names: List[str]
    error_message: str = "Processing failed for the entire batch."
    results: List[ParsedNameResult] = []  # Empty results list for consistency

    def generate_failed_results(self) -> List[dict[str, Any]]:
        failed_list: List[dict[str, Any]] = []
        for name in self.batch_input_names:
            failed_item = ParsedNameResult(
                original_name=name,
                error_message=self.error_message,
                parsing_method="Batch Failed"
            )
            failed_list.append(failed_item.to_dict())
        return failed_list