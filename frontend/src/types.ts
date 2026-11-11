export type CheckStatus = 'pass' | 'warning' | 'fail' | 'info';

export interface Check {
  name: string;
  status: CheckStatus;
  value?: string;
  recommendation?: string;
}

export interface SEOResult {
  score: number;
  title?: string;
  description?: string;
  checks: Check[];
  error?: string;
}

export interface PerformanceScores {
  performance?: number;
  accessibility?: number;
  best_practices?: number;
  seo?: number;
}

export interface PerformanceMetric {
  name: string;
  value: string;
  status: string;
}

export interface PerformanceResult {
  score?: number;
  scores?: PerformanceScores;
  metrics: PerformanceMetric[];
  strategy: string;
  error?: string;
}

export interface SecurityResult {
  score: number;
  is_https: boolean;
  ssl_valid?: boolean;
  ssl_expiry_days?: number;
  ssl_issuer?: string;
  checks: Check[];
  error?: string;
}

export interface ContentResult {
  score: number;
  word_count?: number;
  reading_time_minutes?: number;
  internal_links?: number;
  external_links?: number;
  total_images?: number;
  images_missing_alt?: number;
  checks: Check[];
  error?: string;
}

export interface AnalysisResult {
  url: string;
  overall_score: number;
  seo: SEOResult;
  performance: PerformanceResult;
  security: SecurityResult;
  content: ContentResult;
  analyzed_at: string;
  response_time_ms?: number;
  http_status?: number;
}
