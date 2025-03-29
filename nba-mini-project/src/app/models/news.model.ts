export interface News {
    id: number;
    title: string;
    category: string;
    summary: string;
    content?: string;
    time: string;
    image_url?: string;
  }
  
  export interface NewsListResponse {
    items: News[];
    total: number;
    page: number;
    size: number;
    pages: number;
  }