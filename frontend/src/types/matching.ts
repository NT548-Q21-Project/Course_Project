import { CV } from "./cv";
import { Job } from "./job";

export interface MatchResult {
  id: string;
  cv_id: string;
  job_id: string;
  candidate_id: string;
  fit_level: "strong_fit" | "fit" | "weak_fit" | "not_fit";
  strengths?: string[] | null;
  weaknesses?: string[] | null;
  suggestions?: string | null;
  score?: number;
  explanation?: string;
  job?: Job;
  cv?: CV;
}
