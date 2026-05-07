export type JobType = "full_time" | "part_time" | "internship" | "full-time" | "contract";
export type JobStatus = "draft" | "active" | "closed" | "expired";

export interface Job {
  id: string;
  recruiter_id: string;
  title: string;
  description: string;
  requirements?: string;
  nice_to_have?: string;
  responsibilities?: string;
  benefits?: string;
  location?: string;
  job_type?: JobType;
  status: JobStatus;
  applications_count?: number;
  created_at: string;
  expired_at?: string;
}
