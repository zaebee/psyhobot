import { Component, OnInit } from '@angular/core';
import { Dialog } from '../dialog';

@Component({
  selector: 'app-dialog-list',
  templateUrl: './dialog-list.component.html',
  styleUrls: ['./dialog-list.component.sass']
})
export class DialogListComponent implements OnInit {

  dialogs: Dialog[] = [];

  constructor() { }

  ngOnInit() {
  }

}
