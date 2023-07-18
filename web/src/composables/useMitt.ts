import mitt from "mitt";

export interface Event {
  title: string,
  message: string,
  error?: boolean
}

type Events = {
  notify: Event
}

export const emitter = mitt<Events>();
