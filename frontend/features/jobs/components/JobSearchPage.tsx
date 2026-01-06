"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, MapPin, Loader2, Filter } from "lucide-react";
import { JobCard } from "./JobCard";
import { SalaryJobTypeFilters } from "./SalaryJobTypeFilters";
import { searchJobsBasicAction, BasicJobSearchResult } from "../actions";

export function JobSearchPage() {
    const router = useRouter();
    const searchParams = useSearchParams();

    // Basic Search State
    const [keyword, setKeyword] = useState(searchParams.get("keyword") || "");
    const [location, setLocation] = useState(searchParams.get("location") || "all");

    // Advanced Filters State
    const [minSalary, setMinSalary] = useState<number | undefined>(
        searchParams.get("min_salary") ? parseInt(searchParams.get("min_salary")!) : undefined
    );
    const [maxSalary, setMaxSalary] = useState<number | undefined>(
        searchParams.get("max_salary") ? parseInt(searchParams.get("max_salary")!) : undefined
    );
    const [jobTypes, setJobTypes] = useState<string[]>(
        searchParams.getAll("job_types") || []
    );
    const [skills, setSkills] = useState<string[]>(
        searchParams.getAll("skills") || []
    );
    const [benefits, setBenefits] = useState<string[]>(
        searchParams.getAll("benefits") || []
    );

    // UI State
    const [results, setResults] = useState<BasicJobSearchResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [showMobileFilters, setShowMobileFilters] = useState(false);

    const itemsPerPage = 20;

    // Perform search
    const performSearch = async (
        page: number = 1,
        searchKeyword: string = keyword,
        searchLocation: string = location,
        searchMinSalary: number | undefined = minSalary,
        searchMaxSalary: number | undefined = maxSalary,
        searchJobTypes: string[] = jobTypes,
        searchSkills: string[] = skills,
        searchBenefits: string[] = benefits
    ) => {
        setLoading(true);
        const offset = (page - 1) * itemsPerPage;

        const result = await searchJobsBasicAction({
            keyword: searchKeyword || undefined,
            location: (searchLocation && searchLocation !== "all") ? searchLocation : undefined,
            min_salary: searchMinSalary,
            max_salary: searchMaxSalary,
            job_types: searchJobTypes,
            skills: searchSkills,
            benefits: searchBenefits,
            limit: itemsPerPage,
            offset,
        });

        setResults(result);
        setLoading(false);
        setCurrentPage(page);

        // Update URL
        const params = new URLSearchParams();
        if (searchKeyword) params.set("keyword", searchKeyword);
        if (searchLocation && searchLocation !== "all") params.set("location", searchLocation);
        if (searchMinSalary) params.set("min_salary", searchMinSalary.toString());
        if (searchMaxSalary) params.set("max_salary", searchMaxSalary.toString());
        searchJobTypes.forEach(t => params.append("job_types", t));
        searchSkills.forEach(s => params.append("skills", s));
        searchBenefits.forEach(b => params.append("benefits", b));
        if (page > 1) params.set("page", page.toString());

        router.push(`?${params.toString()}`, { scroll: false });
    };

    // Trigger search on mount (separate effect to handle potential hydration mismatch if we read params directly in render)
    useEffect(() => {
        performSearch(
            parseInt(searchParams.get("page") || "1"),
            searchParams.get("keyword") || "",
            searchParams.get("location") || "all",
            searchParams.get("min_salary") ? parseInt(searchParams.get("min_salary")!) : undefined,
            searchParams.get("max_salary") ? parseInt(searchParams.get("max_salary")!) : undefined,
            searchParams.getAll("job_types") || [],
            searchParams.getAll("skills") || [],
            searchParams.getAll("benefits") || []
        );
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleSearchFormSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        performSearch(1, keyword, location, minSalary, maxSalary, jobTypes, skills, benefits);
    };

    const handleApplyFilters = (filters: { minSalary?: number; maxSalary?: number; jobTypes: string[]; skills: string[]; benefits: string[] }) => {
        setMinSalary(filters.minSalary);
        setMaxSalary(filters.maxSalary);
        setJobTypes(filters.jobTypes);
        setSkills(filters.skills);
        setBenefits(filters.benefits);
        performSearch(1, keyword, location, filters.minSalary, filters.maxSalary, filters.jobTypes, filters.skills, filters.benefits);
        setShowMobileFilters(false);
    };

    const handleClearFilters = () => {
        setMinSalary(undefined);
        setMaxSalary(undefined);
        setJobTypes([]);
        setSkills([]);
        setBenefits([]);
        performSearch(1, keyword, location, undefined, undefined, [], [], []);
    };

    const totalPages = results ? Math.ceil(results.total / itemsPerPage) : 0;

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold tracking-tight">Tìm kiếm việc làm</h1>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Sidebar Filters (Desktop) */}
                <div className="hidden lg:block lg:col-span-1 space-y-4">
                    <SalaryJobTypeFilters
                        minSalary={minSalary}
                        maxSalary={maxSalary}
                        jobTypes={jobTypes}
                        skills={skills}
                        benefits={benefits}
                        onApply={handleApplyFilters}
                        onClear={handleClearFilters}
                    />
                </div>

                {/* Mobile Filter Toggle */}
                <div className="lg:hidden">
                    <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => setShowMobileFilters(!showMobileFilters)}
                    >
                        <Filter className="mr-2 h-4 w-4" />
                        {showMobileFilters ? "Ẩn bộ lọc" : "Hiện bộ lọc nâng cao"}
                    </Button>

                    {showMobileFilters && (
                        <div className="mt-4 p-4 bg-white border rounded-lg shadow-sm">
                            <SalaryJobTypeFilters
                                minSalary={minSalary}
                                maxSalary={maxSalary}
                                jobTypes={jobTypes}
                                skills={skills}
                                benefits={benefits}
                                onApply={handleApplyFilters}
                                onClear={handleClearFilters}
                            />
                        </div>
                    )}
                </div>

                {/* Main Content */}
                <div className="lg:col-span-3 space-y-6">
                    {/* Search Form */}
                    <form onSubmit={handleSearchFormSubmit} className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {/* Keyword Input */}
                            <div className="md:col-span-2">
                                <div className="relative">
                                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        type="text"
                                        placeholder="Tìm kiếm theo từ khóa..."
                                        value={keyword}
                                        onChange={(e) => setKeyword(e.target.value)}
                                        className="pl-10"
                                    />
                                </div>
                            </div>

                            {/* Location Select */}
                            <div>
                                <div className="relative">
                                    <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground z-10" />
                                    <Select value={location} onValueChange={setLocation}>
                                        <SelectTrigger className="pl-10">
                                            <SelectValue placeholder="Tất cả địa điểm" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="all">Tất cả địa điểm</SelectItem>
                                            <SelectItem value="remote">Remote</SelectItem>
                                            <SelectItem value="hybrid">Hybrid</SelectItem>
                                            <SelectItem value="on-site">Tại văn phòng</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>
                        </div>

                        {/* Search Button */}
                        <div className="mt-4 flex justify-end">
                            <Button type="submit" disabled={loading} className="w-full md:w-auto px-8">
                                {loading ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Đang tìm kiếm...
                                    </>
                                ) : (
                                    <>
                                        <Search className="mr-2 h-4 w-4" />
                                        Tìm kiếm
                                    </>
                                )}
                            </Button>
                        </div>
                    </form>

                    {/* Results */}
                    {loading ? (
                        <div className="flex justify-center items-center py-12">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : results ? (
                        <>
                            {/* Results Header */}
                            <div className="flex items-center justify-between">
                                <p className="text-sm text-muted-foreground">
                                    Tìm thấy <span className="font-semibold text-foreground">{results.total}</span> công việc
                                </p>
                            </div>

                            {/* Job List */}
                            {results.items.length > 0 ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                                    {results.items.map((job) => (
                                        <div key={job.id} className="h-full">
                                            <JobCard {...job} />
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-12 bg-white rounded-lg border">
                                    <p className="text-lg font-medium text-muted-foreground">
                                        Không tìm thấy tin tuyển dụng nào phù hợp
                                    </p>
                                    <p className="text-sm text-muted-foreground mt-2">
                                        Thử thay đổi từ khóa hoặc bộ lọc để tìm kiếm
                                    </p>
                                    <Button variant="link" onClick={handleClearFilters} className="mt-2">
                                        Xóa tất cả bộ lọc
                                    </Button>
                                </div>
                            )}

                            {/* Pagination */}
                            {totalPages > 1 && (
                                <div className="flex justify-center gap-2 mt-6">
                                    <Button
                                        variant="outline"
                                        onClick={() => performSearch(currentPage - 1, keyword, location, minSalary, maxSalary, jobTypes)}
                                        disabled={currentPage === 1 || loading}
                                    >
                                        Trang trước
                                    </Button>
                                    <div className="flex items-center gap-2">
                                        <span className="text-sm text-muted-foreground">
                                            Trang {currentPage} / {totalPages}
                                        </span>
                                    </div>
                                    <Button
                                        variant="outline"
                                        onClick={() => performSearch(currentPage + 1, keyword, location, minSalary, maxSalary, jobTypes)}
                                        disabled={currentPage === totalPages || loading}
                                    >
                                        Trang sau
                                    </Button>
                                </div>
                            )}
                        </>
                    ) : null}
                </div>
            </div>
        </div>
    );
}
