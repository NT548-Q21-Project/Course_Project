import React, { useEffect, useState } from "react";
import { ClipboardList, Briefcase, Calendar, ChevronRight, FileText, CheckCircle2, Clock, XCircle } from "lucide-react";
import { Link } from "react-router-dom";
import { applicationApi } from "../../services/applicationApi";
import { jobApi } from "../../services/jobApi";
import { cvApi } from "../../services/cvApi";
import { Application } from "../../types/application";
import { Job } from "../../types/job";
import { CV } from "../../types/cv";
import { formatDate, cn } from "../../utils";

const getStatusStyle = (status: string) => {
  switch (status) {
    case "accepted":
      return "bg-green-100 text-green-700";
    case "rejected":
      return "bg-red-100 text-red-700";
    case "submitted":
      return "bg-yellow-100 text-yellow-700";
    default:
      return "bg-gray-100 text-gray-600";
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case "accepted":
      return <CheckCircle2 size={12} />;
    case "rejected":
      return <XCircle size={12} />;
    default:
      return <Clock size={12} />;
  }
};

const CandidateApplicationsPage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [jobsById, setJobsById] = useState<Record<string, Job>>({});
  const [cvsById, setCvsById] = useState<Record<string, CV>>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        const appData = await applicationApi.getMyApplications();
        setApplications(appData);

        const uniqueJobIds = [...new Set(appData.map((app) => app.job_id))];
        const [jobResults, cvs] = await Promise.all([
          Promise.all(uniqueJobIds.map((jobId) => jobApi.getJob(jobId))),
          cvApi.getCVs(),
        ]);

        setJobsById(
          jobResults.reduce<Record<string, Job>>((accumulator, job) => {
            accumulator[job.id] = job;
            return accumulator;
          }, {})
        );
        setCvsById(
          cvs.reduce<Record<string, CV>>((accumulator, cv) => {
            accumulator[cv.id] = cv;
            return accumulator;
          }, {})
        );
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchApplications();
  }, []);

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-black text-gray-900 tracking-tight uppercase">My Applications</h2>
          <p className="text-gray-500 font-bold uppercase tracking-widest text-xs mt-1">
            Track your journey and application status in real-time
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4">
          {[1, 2, 3].map((i) => <div key={i} className="h-24 bg-gray-100 animate-pulse rounded-3xl" />)}
        </div>
      ) : applications.length === 0 ? (
        <div className="bg-white rounded-3xl p-16 border border-dashed border-gray-200 text-center space-y-6">
          <div className="w-24 h-24 bg-gray-50 text-gray-300 rounded-full flex items-center justify-center mx-auto">
            <ClipboardList size={48} />
          </div>
          <div className="max-w-sm mx-auto">
            <h3 className="text-xl font-bold text-gray-900">No applications yet</h3>
            <p className="text-gray-500 mt-2 font-medium">
              Start applying to jobs to see your application history here.
            </p>
          </div>
          <Link
            to="/candidate/jobs"
            className="inline-flex items-center gap-2 px-8 py-3 bg-blue-600 text-white font-black text-sm uppercase tracking-widest rounded-2xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-100"
          >
            Browse Jobs <ChevronRight size={18} />
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="px-6 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Target Role</th>
                <th className="px-6 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">CV</th>
                <th className="px-6 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Applied At</th>
                <th className="px-6 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {applications.map((app) => {
                const job = jobsById[app.job_id];
                const cv = cvsById[app.cv_id];

                return (
                  <tr key={app.id} className="hover:bg-gray-50/50 transition-colors group">
                    <td className="px-6 py-6">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center shrink-0">
                          <Briefcase size={20} />
                        </div>
                        <div>
                          <Link to={`/candidate/jobs/${app.job_id}`} className="font-bold text-gray-900 hover:text-blue-600 transition-colors block leading-tight mb-1">
                            {job?.title || app.job_id}
                          </Link>
                          <p className="text-xs text-gray-500 font-bold">{job?.location || "Backend application"}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-6 font-bold text-xs text-gray-600">
                      <div className="flex items-center gap-2">
                        <FileText size={14} className="text-blue-400" />
                        {cv?.title || cv?.file_name || app.cv_id}
                      </div>
                    </td>
                    <td className="px-6 py-6">
                      <div className="flex items-center gap-2 text-xs text-gray-500 font-bold">
                        <Calendar size={14} />
                        {formatDate(app.applied_at)}
                      </div>
                    </td>
                    <td className="px-6 py-6">
                      <span className={cn(
                        "inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest",
                        getStatusStyle(app.status)
                      )}>
                        {getStatusIcon(app.status)}
                        {app.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default CandidateApplicationsPage;