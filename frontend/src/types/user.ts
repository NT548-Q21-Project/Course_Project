export type UserRole = "candidate" | "recruiter";

export interface User {
  id: string;
  auth_id: string;
  email: string;
  full_name?: string;
  role: UserRole;
  created_at: string;
}

export interface CandidateProfile {
  id: string;
  user_id: string;
  full_name: string;
}

export interface RecruiterProfile {
  id: string;
  user_id: string;
  full_name: string;
}
