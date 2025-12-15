// Types for widgets
export type Place = {
  id: string;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  rating: number;
  description?: string;
};
  
export type Trip = {
  id: string;
  name: string;
  center_latitude: number;
  center_longitude: number;
  zoom_level?: number | 13; 
  places: Place[];
};

export type SearchProgress = {
  query: string;
  done: boolean;
};

export type AgentState = {
  trips: Trip[];
  selected_trip_id: string | null;
  search_progress?: SearchProgress[];
};