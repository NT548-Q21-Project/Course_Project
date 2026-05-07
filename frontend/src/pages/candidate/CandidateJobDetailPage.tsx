import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ChevronLeft, MapPin, Briefcase, Building2, Sparkles, CheckCircle2, ChevronRight, Loader2, Trophy, Target as TargetIcon, FileCheck } from "lucide-react";
import { motion } from "motion/react";
import { jobApi } from "../../services/jobApi";
import { cvApi } from "../../services/cvApi";
import { matchingApi } from "../../services/matchingApi";
import { applicationApi } from "../../services/applicationApi";
import { extractTextFromPDF } from "../../utils/pdfExtractor";
import { Job } from "../../types/job";
import { CV } from "../../types/cv";
import { MatchResult } from "../../types/matching";
import { cn, getMatchScoreColor } from "../../utils";

const CandidateJobDetailPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();

  const [job, setJob] = useState<Job | null>(null);
  const [cvs, setCvs] = useState<CV[]>([]);
  const [selectedCvId, setSelectedCvId] = useState<string>("");
  const [cvText, setCvText] = useState("");
  const [cvTextDirty, setCvTextDirty] = useState(false);
  const [isLoadingPdf, setIsLoadingPdf] = useState(false);
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isMatching, setIsMatching] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [applied, setApplied] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      if (!jobId) return;
      try {
        const [jobData, cvsData] = await Promise.all([
          jobApi.getJob(jobId),
          cvApi.getCVs()
        ]);
        setJob(jobData);
        setCvs(cvsData);
        if (cvsData.length > 0) {
          setSelectedCvId(cvsData[0].id);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, [jobId]);

  // Extract text from PDF when selected CV changes (unless text was manually edited)
  useEffect(() => {
    if (cvTextDirty) return;

    const selectedCv = cvs.find((cv) => cv.id === selectedCvId);
    if (!selectedCv || !selectedCv.file_url) {
      setCvText("");
      return;
    }

    const extractText = async () => {
      setIsLoadingPdf(true);
      try {
        const extractedText = await extractTextFromPDF(selectedCv.file_url);
        setCvText(extractedText);
      } catch (error) {
        console.error("Failed to extract PDF text:", error);
        // Fallback: use CV metadata
        setCvText(`CV: ${selectedCv.title}\nFile: ${selectedCv.file_name}`);
      } finally {
        setIsLoadingPdf(false);
      }
    };

    extractText();
  }, [cvs, selectedCvId, cvTextDirty]);

  const handleMatch = async () => {
    if (!jobId || !selectedCvId || !job || cvText.trim().length < 20) return;
    setIsMatching(true);
    setMatchResult(null);
    try {
      const result = await matchingApi.matchCVWithJob({
        cv_id: selectedCvId,
        job_id: jobId,
        cv_text: cvText,
        job_title: job.title,
        job_description: job.description,
        responsibilities: job.responsibilities,
        requirements: job.requirements,
        nice_to_have: job.nice_to_have,
        benefits: job.benefits,
      });
      setMatchResult(result);
    } catch (err) {
      console.error(err);
    } finally {
      setIsMatching(false);
    }
  };

  const handleApply = async () => {
    if (!jobId || !selectedCvId) return;
    setIsApplying(true);
    try {
      await applicationApi.apply({
        job_id: jobId,
        cv_id: selectedCvId
      });
      setApplied(true);
    } catch (err) {
      console.error(err);
    } finally {
      setIsApplying(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <Loader2 className="animate-spin text-blue-600 mb-4" size={48} />
        <p className="text-gray-500 font-bold uppercase tracking-widest text-xs">Loading Opportunity Details...</p>
      </div>
    );
  }

  if (!job) return <div>Job not found.</div>;

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-gray-500 font-bold hover:text-blue-600 transition-colors uppercase text-xs tracking-widest"
      >
        <ChevronLeft size={16} /> Back to Search
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-8 space-y-8">
          <div className="bg-white rounded-3xl p-8 border border-gray-100 shadow-sm relative overflow-hidden">
            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-4">
                <span className="px-3 py-1 bg-blue-50 text-blue-700 text-[10px] font-black uppercase tracking-widest rounded-lg">
                  Featured Role
                </span>
                <span className={cn(
                  "px-3 py-1 text-[10px] font-black uppercase tracking-widest rounded-lg",
                  job.status === "active" ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"
                )}>
                  {job.status}
                </span>
              </div>

              <h2 className="text-3xl font-black text-gray-900 mb-4 tracking-tight uppercase leading-tight">
                {job.title}
              </h2>

              <div className="flex flex-wrap items-center gap-x-8 gap-y-4 mb-8">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gray-50 rounded-xl flex items-center justify-center border border-gray-100">
                    <Building2 className="text-gray-400" size={20} />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Company</p>
                    <p className="font-bold text-gray-900">Global Tech Solutions</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gray-50 rounded-xl flex items-center justify-center border border-gray-100">
                    <MapPin className="text-gray-400" size={20} />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Location</p>
                    <p className="font-bold text-gray-900">{job.location}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gray-50 rounded-xl flex items-center justify-center border border-gray-100">
                    <Briefcase className="text-gray-400" size={20} />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Job Type</p>
                    <p className="font-bold text-gray-900">Full-time</p>
                  </div>
                </div>
              </div>

              <div className="prose prose-blue max-w-none text-gray-600 space-y-10">
                <div>
                  <h3 className="text-lg font-black text-gray-900 uppercase tracking-tight mb-4">Job Description</h3>
                  <p className="leading-relaxed bg-gray-50 border border-gray-100 p-6 rounded-3xl font-medium">{job.description}</p>
                </div>

                <div>
                  <h3 className="text-lg font-black text-gray-900 uppercase tracking-tight mb-4">Responsibilities</h3>
                  {(!job.responsibilities || job.responsibilities.trim() === "") ? (
                    <p className="text-sm text-gray-500 italic">No responsibilities provided</p>
                  ) : (
                    <ul className="space-y-3 list-none p-0 m-0">
                      {job.responsibilities.split(/[;\n]/).filter(r => r.trim()).map((resp, i) => (
                        <li key={i} className="flex items-start gap-4 text-gray-700">
                          <CheckCircle2 size={20} className="text-blue-500 shrink-0 mt-0.5" />
                          <span className="font-medium leading-relaxed">{resp.trim()}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <div>
                  <h3 className="text-lg font-black text-gray-900 uppercase tracking-tight mb-4">Requirements</h3>
                  {(!job.requirements || job.requirements.trim() === "") ? (
                    <p className="text-sm text-gray-500 italic">No requirements provided</p>
                  ) : (
                    <ul className="space-y-3 list-none p-0 m-0">
                      {job.requirements.split(/[;\n]/).filter(r => r.trim()).map((req, i) => (
                        <li key={i} className="flex items-start gap-4 text-gray-700">
                          <CheckCircle2 size={20} className="text-blue-500 shrink-0 mt-0.5" />
                          <span className="font-medium leading-relaxed">{req.trim()}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <div>
                  <h3 className="text-lg font-black text-gray-900 uppercase tracking-tight mb-4">Nice to Have</h3>
                  {(!job.nice_to_have || job.nice_to_have.trim() === "") ? (
                    <p className="text-sm text-gray-500 italic">No nice-to-have skills provided</p>
                  ) : (
                    <ul className="space-y-3 list-none p-0 m-0">
                      {job.nice_to_have.split(/[;\n]/).filter(r => r.trim()).map((req, i) => (
                        <li key={i} className="flex items-start gap-4 text-gray-700">
                          <CheckCircle2 size={20} className="text-blue-500 shrink-0 mt-0.5" />
                          <span className="font-medium leading-relaxed">{req.trim()}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <div>
                  <h3 className="text-lg font-black text-gray-900 uppercase tracking-tight mb-4">Benefits</h3>
                  {(!job.benefits || job.benefits.trim() === "") ? (
                    <p className="text-sm text-gray-500 italic">No benefits provided</p>
                  ) : (
                    <ul className="space-y-3 list-none p-0 m-0">
                      {job.benefits.split(/[;\n]/).filter(b => b.trim()).map((ben, i) => (
                        <li key={i} className="flex items-start gap-4 text-gray-700">
                          <CheckCircle2 size={20} className="text-blue-500 shrink-0 mt-0.5" />
                          <span className="font-medium leading-relaxed">{ben.trim()}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
            <div className="absolute right-0 bottom-0 opacity-5 grayscale pointer-events-none p-8">
              <Building2 size={240} />
            </div>
          </div>
        </div>

        {/* Sidebar / Sidebar AI matching */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm sticky top-24">
            <div className="flex items-center gap-2 mb-6">
              <Sparkles className="text-blue-600" size={24} />
              <h3 className="text-xl font-black text-gray-900 uppercase tracking-tight">AI Matching</h3>
            </div>

            {applied ? (
              <div className="text-center py-8 bg-green-50 rounded-2xl border border-green-100 space-y-4">
                <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto ring-8 ring-green-50">
                  <FileCheck size={32} />
                </div>
                <div>
                  <h4 className="text-lg font-black text-green-900 uppercase tracking-tight">Success!</h4>
                  <p className="text-green-700 text-sm font-medium">Your application has been sent.</p>
                </div>
                <Link to="/candidate/applications" className="inline-block text-green-700 font-bold underline text-sm">
                  Track my applications
                </Link>
              </div>
            ) : (
              <div className="space-y-6">
                <div>
                  <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">Select your CV</label>
                  <select
                    value={selectedCvId}
                    onChange={(e) => {
                      setSelectedCvId(e.target.value);
                      setCvTextDirty(false);
                    }}
                    className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none font-bold text-gray-900 transition-all mb-4"
                  >
                    {cvs.map(cv => (
                      <option key={cv.id} value={cv.id}>{cv.title}</option>
                    ))}
                  </select>

                  <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">CV Text for Analysis {isLoadingPdf && <span className="text-blue-500">(Extracting from PDF...)</span>}</label>
                  <textarea
                    value={cvText}
                    onChange={(e) => {
                      setCvText(e.target.value);
                      setCvTextDirty(true);
                    }}
                    rows={8}
                    disabled={isLoadingPdf}
                    className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none font-medium text-gray-900 transition-all mb-4 resize-none disabled:opacity-50"
                    placeholder="PDF text will be extracted and displayed here. Edit manually if needed."
                  />

                  <button
                    onClick={handleMatch}
                    disabled={isMatching || isLoadingPdf || cvs.length === 0 || cvText.trim().length < 20}
                    className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-gray-900 text-white rounded-2xl font-black text-sm uppercase tracking-widest hover:bg-black transition-all active:scale-[0.98] disabled:opacity-50"
                  >
                    {isMatching ? <Loader2 className="animate-spin" size={20} /> : <TargetIcon size={20} />}
                    Check Match Score
                  </button>
                </div>

                {matchResult && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-6 pt-6 border-t border-gray-100"
                  >
                    <div className="flex flex-col items-center text-center p-6 bg-gray-50 rounded-3xl border border-gray-100 relative overflow-hidden">
                      <div className="relative z-10">
                        <div className={cn(
                          "text-4xl font-black mb-1 drop-shadow-sm",
                          getMatchScoreColor(matchResult.score).split(' ')[0]
                        )}>
                          {matchResult.score}%
                        </div>
                        <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">Matching Score</p>
                        <p className="text-xs font-bold mt-2 text-gray-600 px-4">
                          {matchResult.score >= 80 ? "STRONG MATCH" : matchResult.score >= 60 ? "GOOD MATCH" : "WEAK MATCH"}
                        </p>
                      </div>
                      <div className="absolute top-0 right-0 p-4 opacity-10">
                        <Trophy size={64} />
                      </div>
                    </div>



                    <div className="grid grid-cols-1 gap-4">
                      <div className="p-4 bg-emerald-50/50 rounded-2xl border border-emerald-100">
                        <h4 className="text-[10px] font-black text-emerald-600 uppercase tracking-widest mb-2 px-1">Strengths</h4>
                        <ul className="space-y-1">
                          {(matchResult.strengths ?? []).length > 0 ? (
                            (matchResult.strengths ?? []).map((s, i) => (
                              <li key={i} className="text-[10px] font-bold text-gray-700 flex gap-2">
                                <div className="mt-1.5 w-1 h-1 bg-emerald-400 rounded-full shrink-0" />
                                {s}
                              </li>
                            ))
                          ) : (
                            <li className="text-[10px] text-gray-400 italic">No strengths available</li>
                          )}
                        </ul>
                      </div>
                      <div className="p-4 bg-orange-50/50 rounded-2xl border border-orange-100">
                        <h4 className="text-[10px] font-black text-orange-600 uppercase tracking-widest mb-2 px-1">Weaknesses</h4>
                        <ul className="space-y-1">
                          {(matchResult.weaknesses ?? []).length > 0 ? (
                            (matchResult.weaknesses ?? []).map((w, i) => (
                              <li key={i} className="text-[10px] font-bold text-gray-700 flex gap-2">
                                <div className="mt-1.5 w-1 h-1 bg-orange-400 rounded-full shrink-0" />
                                {w}
                              </li>
                            ))
                          ) : (
                            <li className="text-[10px] text-gray-400 italic">No weaknesses available</li>
                          )}
                        </ul>
                      </div>
                    </div>

                    <p className="text-xs text-gray-500 italic p-4 bg-blue-50/50 rounded-2xl border border-blue-100 leading-relaxed">
                      "{matchResult.explanation}"
                    </p>
                  </motion.div>
                )}

                <div className="pt-6 border-t border-gray-100 space-y-2">
                  <button
                    onClick={handleApply}
                    disabled={isApplying || !selectedCvId}
                    className="w-full flex items-center justify-center gap-2 py-4 px-4 bg-blue-600 text-white rounded-3xl font-black text-lg uppercase tracking-tight hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-200 transition-all active:scale-[0.98] disabled:opacity-50"
                  >
                    {isApplying ? <Loader2 className="animate-spin" size={24} /> : (
                      <>APPLY NOW <ChevronRight size={24} /></>
                    )}
                  </button>
                  {!selectedCvId && cvs.length > 0 && (
                    <p className="text-[10px] text-center font-bold text-red-500 uppercase tracking-widest">Select a CV to apply.</p>
                  )}
                </div>

                {cvs.length === 0 && (
                  <div className="p-4 bg-yellow-50 rounded-2xl border border-yellow-100 text-center">
                    <p className="text-sm text-yellow-800 font-bold mb-3">You need a CV to match or apply.</p>
                    <Link to="/candidate/cvs" className="text-blue-600 font-black text-xs uppercase tracking-widest hover:underline">
                      Upload your first CV
                    </Link>
                  </div>
                )}
              </div>
            )}
          </div>


        </div>
      </div>
    </div>
  );
};

export default CandidateJobDetailPage;
