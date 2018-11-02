import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { MatButtonModule, MatCardModule, MatIconModule, MatTabsModule, MatSidenavModule, MatListModule,
MatFormFieldModule, MatSelectModule, MatInputModule, MatToolbarModule } from '@angular/material';

@NgModule({
  imports: [MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatTabsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatToolbarModule,
    MatSidenavModule,
    MatListModule,
    MatInputModule],
  exports: [MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatTabsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatToolbarModule,
    MatSidenavModule,
    MatListModule,
    MatInputModule]
})
export class MaterialModule { }
