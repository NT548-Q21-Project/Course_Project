import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Building2, ChevronRight, FileText, ClipboardList, MapPin, Search, Sparkles, X } from "lucide-react";
import { jobApi } from "../../services/jobApi";
import { Job } from "../../types/job";
import { cn, formatDate } from "../../utils";

const formatJobType = (jobType?: string) => {
  switch (jobType) {
    case "full_time":
    case "full-time":
      return "Full-time";
    case "part_time":
    case "part-time":
      return "Part-time";
    case "internship":
      return "Internship";
    default:
      return "Unknown";
  }
};

const CandidateHomePage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState({
    location: "",
    job_type: "",
    status: "active",
  });

  useEffect(() => {
    const loadJobs = async () => {
      try {
        setIsLoading(true);
        const data = await jobApi.getJobs(filters);
        setJobs(data);
      } catch (error) {
        console.error("Failed to load jobs:", error);
        setJobs([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadJobs();
  }, [filters]);

  const filteredJobs = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) {
      return jobs;
    }

    return jobs.filter((job) => {
      return [job.title, job.description, job.location, job.job_type]
        .filter(Boolean)
        .some((field) => field?.toLowerCase().includes(query));
    });
  }, [jobs, searchQuery]);

  return (
    <div className="space-y-8">
      <section className="relative overflow-hidden rounded-3xl bg-emerald-600 p-8 text-white shadow-xl shadow-emerald-100">
        <div className="relative z-10 max-w-2xl">
          <h2 className="mb-4 text-3xl font-black tracking-tighter">Find your next career move with AI</h2>
          <p className="mb-6 text-lg font-medium leading-relaxed text-emerald-50">
            Browse live jobs from the backend and use AI matching to compare your CV against real openings.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link
              to="/candidate/cvs"
              className="flex items-center gap-2 rounded-2xl bg-white px-6 py-3 text-xs font-bold uppercase tracking-widest text-emerald-600 shadow-sm transition-all hover:bg-emerald-50 active:scale-[0.98]"
            >
              <FileText size={18} />
              Manage My CVs
            </Link>
            <Link
              to="/candidate/applications"
              className="flex items-center gap-2 rounded-2xl border border-emerald-500 bg-emerald-700 px-6 py-3 text-xs font-bold uppercase tracking-widest text-white transition-all hover:bg-emerald-800 active:scale-[0.98]"
            >
              <ClipboardList size={18} />
              My Applications
            </Link>
          </div>
        </div>
        <div className="pointer-events-none absolute right-0 top-0 bottom-0 w-1/3 opacity-10">
          <Sparkles size={300} className="-mr-20 -mt-20" />
        </div>
      </section>

      <div className="space-y-4 rounded-3xl border border-gray-100 bg-white p-4 shadow-sm md:p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center">
          <div className="relative w-full flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search by title, description, location, or job type..."
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              className="w-full rounded-2xl border-none bg-gray-50 py-3 pl-12 pr-4 font-bold text-gray-900 outline-none transition-all placeholder:text-gray-400 focus:bg-white focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div className="flex w-full items-center gap-2 overflow-x-auto pb-1 md:w-auto md:pb-0">
            <select
              value={filters.location}
              onChange={(event) => setFilters({ ...filters, location: event.target.value })}
              className="min-w-35 cursor-pointer rounded-2xl border-none bg-gray-50 px-4 py-3 text-sm font-bold text-gray-700 outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="">All Locations</option>
              <option value="Remote">Remote</option>
              <option value="Singapore">Singapore</option>
              <option value="London">London</option>
              <option value="Hà Nội">Hà Nội</option>
              <option value="Hồ Chí Minh">Hồ Chí Minh</option>
            </select>
            <select
              value={filters.job_type}
              onChange={(event) => setFilters({ ...filters, job_type: event.target.value })}
              className="min-w-35 cursor-pointer rounded-2xl border-none bg-gray-50 px-4 py-3 text-sm font-bold text-gray-700 outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="">Job Type</option>
              <option value="full_time">Full-time</option>
              <option value="part_time">Part-time</option>
              <option value="internship">Internship</option>
            </select>
            {(searchQuery || filters.location || filters.job_type) && (
              <button
                type="button"
                onClick={() => {
                  setSearchQuery("");
                  setFilters({ location: "", job_type: "", status: "active" });
                }}
                className="rounded-2xl bg-red-50 p-3 text-red-600 transition-colors hover:bg-red-100"
                title="Clear Filters"
              >
                <X size={20} />
              </button>
            )}
          </div>
        </div>
        <div className="flex items-center justify-between px-2">
          <p className="text-sm font-bold uppercase tracking-widest text-gray-500">
            {isLoading ? "Loading jobs..." : `${filteredJobs.length} Positions Found`}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 pb-12 md:grid-cols-2 xl:grid-cols-3">
        {isLoading ? (
          Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="h-64 animate-pulse rounded-3xl border border-gray-100 bg-gray-100 shadow-sm" />
          ))
        ) : filteredJobs.length === 0 ? (
          <div className="col-span-full rounded-3xl border-2 border-dashed border-gray-100 bg-white py-20 text-center">
            <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-gray-50 text-gray-300">
              <Search size={32} />
            </div>
            <h3 className="text-xl font-black uppercase text-gray-900">No jobs found</h3>
            <p className="mt-2 font-medium text-gray-500">Try adjusting your filters or search keywords.</p>
            <button
              type="button"
              onClick={() => {
                setSearchQuery("");
                setFilters({ location: "", job_type: "", status: "active" });
              }}
              className="mt-6 text-sm font-black uppercase tracking-widest text-emerald-600 hover:underline"
            >
              Clear all filters
            </button>
          </div>
        ) : (
          filteredJobs.map((job) => (
            <Link
              key={job.id}
              to={`/candidate/jobs/${job.id}`}
              className="group rounded-3xl border border-gray-100 bg-white p-6 shadow-sm transition-all hover:-translate-y-1 hover:border-emerald-100 hover:shadow-2xl active:scale-[0.98]"
            >
              <div className="mb-6 flex items-start justify-between">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-gray-100 bg-gray-50 transition-colors group-hover:bg-emerald-50">
                  <Building2 className="text-gray-400 group-hover:text-emerald-600" size={28} />
                </div>
                <span
                  className={cn(
                    "rounded-lg border px-3 py-1 text-[10px] font-black uppercase tracking-widest",
                    job.status === "active"
                      ? "border-emerald-100 bg-emerald-50 text-emerald-700"
                      : "border-gray-100 bg-gray-50 text-gray-500",
                  )}
                >
                  {job.status}
                </span>
              </div>

              <div className="mb-4">
                <h4 className="mb-2 line-clamp-2 text-lg font-black uppercase tracking-tighter text-gray-900 transition-colors group-hover:text-emerald-600">
                  {job.title}
                </h4>
                <p className="text-sm font-bold uppercase tracking-widest text-gray-400">{job.company_name ?? "Hiring Company"}</p>
              </div>

              <div className="mb-8 flex flex-wrap gap-x-4 gap-y-2 text-xs font-black text-gray-500">
                <div className="flex items-center gap-1.5 rounded-lg bg-gray-50 px-2 py-1">
                  <MapPin size={14} className="text-emerald-500" />
                  {job.location}
                </div>
                <div className="flex items-center gap-1.5 rounded-lg bg-gray-50 px-2 py-1">
                  <Building2 size={14} className="text-emerald-500" />
                  {formatJobType(job.job_type)}
                </div>
              </div>

              <div className="flex items-center justify-between border-t border-gray-50 pt-4">
                <span className="text-[10px] font-black uppercase tracking-widest text-gray-400">
                  {formatDate(job.created_at)}
                </span>
                <div className="flex items-center gap-1 text-xs font-black uppercase tracking-widest text-emerald-600 transition-all group-hover:gap-2">
                  Apply Now <ChevronRight size={16} />
                </div>
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
};

export default CandidateHomePage;
