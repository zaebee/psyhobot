export class Dialog {
  id: number;
  name: string;
  user_id: number;
  text: string;

  constructor(values: Object = {}) {
    Object.assign(this, values);
  }
}
