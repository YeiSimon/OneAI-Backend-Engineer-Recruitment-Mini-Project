import { Component, OnInit } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';
import { NewsService } from '../services/new.service';
import { News, NewsListResponse } from '../models/news.model';

@Component({
  selector: 'app-news-list',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule],
  templateUrl: './news-list.component.html',
  styleUrl: './news-list.component.scss'
})
export class NewsListComponent implements OnInit{

  newsList: News[] = [];
  imageUrls: string[] = [];
  newsResponse: NewsListResponse | null = null;
  loading = true;
  currentPage = 1;
  pageSize = 10;

  constructor(private newsService: NewsService) {}
  
  ngOnInit(): void {
    this.loadNews();
  }

  loadNews(): void {
    this.loading = true;
    this.newsService.getNews(this.currentPage, this.pageSize).subscribe({
      next: (response) => {
        this.newsResponse = response;
        this.newsList = response.items.map(item => ({
          ...item,
          image_url: this.newsService.getFullImageUrl(item.image_url ?? null)
        }));
        this.loading = false;
      },
      error: (error) => {
        console.error('Error fetching news:', error);
        this.loading = false;
      }
    });
  }
  
  loadPage(page: number): void {
    this.currentPage = page;
    this.loadNews();
  }
  // newsList: NewsItem[] = [
  //   {
  //     category: 'NBA',
  //     title: '太陽對戰灰狼8連敗陷危機 杜蘭特：不想沒附加賽可打',
  //     time: '41分鐘 以前',
  //     imageUrl: 'assets/images/suns-wolves.jpg',
  //     summary: '去年例行賽3戰橫掃灰狼的太陽，經過季後賽首輪對戰慘遭剃光頭的恥辱之後，本季對上陣容大幅變化的灰狼...'
  //   },
  //   {
  //     category: 'NBA',
  //     title: '近況火燙！雷納德高效率飆分率籃網 快艇12戰奪10勝',
  //     time: '1小時 以前',
  //     imageUrl: 'assets/images/suns-wolves.jpg',
  //     summary: '對於快艇來說，能否安穩搶下西區前6張季後賽門票，雷納德（Kawhi Leonard）的健康情況和攻...'
  //   }
  // ];
}
