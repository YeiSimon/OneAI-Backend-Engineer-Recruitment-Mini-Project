import { Component, OnInit } from '@angular/core';
import {MatTabsModule} from '@angular/material/tabs';
import { MatButtonModule } from '@angular/material/button';
import {MatToolbarModule} from '@angular/material/toolbar';
import { HttpClient,HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-tabs',
  imports: [
    MatTabsModule, 
    MatButtonModule, 
    MatToolbarModule,
    HttpClientModule],
    
  templateUrl: './tabs.component.html',
  styleUrl: './tabs.component.scss'
})
export class TabsComponent implements OnInit {
  apiStatus: string = 'Unknown';
  apiPort: string = '';
  apiInfo: any = null;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    // You can check API status on component initialization if desired
    // this.checkFastApiPort();
    console.log('TabsComponent initialized');
  }

  checkFastApiPort(): void {
    // Default FastAPI port
    const baseUrl = 'http://localhost:8000';
    
    console.log('Checking FastAPI connection at:', baseUrl);
    
    this.http.get(`${baseUrl}/`).subscribe({
      next: (response: any) => {
        this.apiInfo = response;
        this.apiPort = baseUrl.split(':')[2]; // Extract port number
        this.apiStatus = 'Online';
        console.log('FastAPI Response:', response);
        console.log('Connection successful on port:', this.apiPort);
      },
      error: (error) => {
        console.error('Error connecting to FastAPI:', error);
        console.log('Connection failed on port:', baseUrl.split(':')[2]);
        this.apiStatus = 'Offline';
        this.apiPort = baseUrl.split(':')[2]; // Extract port number
        this.apiInfo = { error: error.message };
        console.log('Error details:', error.message);
      }
    });
  }
}
