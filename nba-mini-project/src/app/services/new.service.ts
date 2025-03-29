import { Injectable } from '@angular/core';
import { HttpClient, HttpParams} from '@angular/common/http';
import { Observable } from 'rxjs';
import { News, NewsListResponse } from '../models/news.model';

@Injectable({
  providedIn: 'root'
})
export class NewsService {
  private apiUrl = 'http://localhost:8000/news'; 
  private imgUrl = 'http://localhost:8000'
  
  constructor(private http: HttpClient) { }
  
  getNews(page: number = 1, size: number = 10): Observable<NewsListResponse> {
    const params = new HttpParams()
      .set('skip', ((page - 1) * size).toString())
      .set('limit', size.toString());
      
    return this.http.get<NewsListResponse>(this.apiUrl, { params })
  }
  
  getNewsById(id: number): Observable<News> {
    return this.http.get<News>(`${this.apiUrl}/${id}`);
  }
  getFullImageUrl(imageUrl: string | null): string {
    if (!imageUrl) {
      return 'https://via.placeholder.com/300x200?text=No+Image';
    }
    
    // If the image URL is already a full URL (starts with http), return it as is
    if (imageUrl.startsWith('http')) {
      return imageUrl;
    }
    
    // Otherwise, prepend the API base URL
    return `${this.imgUrl}${imageUrl}`;
  }
}