import React, { useState, useRef } from 'react';
import {
  GoogleMap,
  useLoadScript,
  Marker,
  InfoWindow
} from '@react-google-maps/api';

// 地图容器拉满父元素
const mapContainerStyle = { width: '100%', height: '100%' };
// 初始中心地点：洛杉矶
const LA_CENTER = { lat: 34.0522, lng: -118.2437 };
// 关闭默认 UI，仅保留缩放控件
const MAP_OPTIONS = { disableDefaultUI: true, zoomControl: true };

export default function LawyerMap({ lawyers }) {
  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: process.env.REACT_APP_GOOGLE_MAPS_API_KEY,
  });
  const [selectedLawyer, setSelectedLawyer] = useState(null);
  const mapRef = useRef();

  if (loadError) return <div className="map-error">Map load error</div>;
  if (!isLoaded) return <div className="map-loading">Loading map…</div>;

  return (
    <GoogleMap
      mapContainerStyle={mapContainerStyle}
      center={LA_CENTER}
      zoom={10}
      options={MAP_OPTIONS}
      onLoad={map => (mapRef.current = map)}
    >
      {lawyers.map(lawyer => (
        <Marker
          key={lawyer.id}
          position={{
            lat: lawyer.latitude,
            lng: lawyer.longitude
          }}
          onClick={() => setSelectedLawyer(lawyer)}
        />
      ))}

      {selectedLawyer && (
        <InfoWindow
          position={{
            lat: selectedLawyer.latitude,
            lng: selectedLawyer.longitude
          }}
          onCloseClick={() => setSelectedLawyer(null)}
        >
          <div className="info-window">
            <h4>{selectedLawyer.name}</h4>
            <p><strong>Specialization:</strong> {selectedLawyer.specialization}</p>
            <p><strong>Address:</strong> {selectedLawyer.address}</p>
            <p><strong>Phone:</strong> {selectedLawyer.phone}</p>
            <p><strong>Rating:</strong> {selectedLawyer.rating}</p>
            <p><strong>Website:</strong> <a href={selectedLawyer.website} target="_blank" rel="noreferrer">{selectedLawyer.website}</a></p>
            <p><strong>Education:</strong> {selectedLawyer.education}</p>
            <p><strong>Awards:</strong> {selectedLawyer.awards}</p>
          </div>
        </InfoWindow>
      )}
    </GoogleMap>
  );
}
