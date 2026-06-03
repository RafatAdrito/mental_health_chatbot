import { useCallback } from "react";
import useStore from "../store";

export function useGeolocation() {
  const requestLocation = useCallback(() => {
    const { setUserLocation, setLocationPermission } = useStore.getState();

    if (!navigator.geolocation) {
      setLocationPermission("unavailable");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
        setLocationPermission("granted");
      },
      () => {
        setLocationPermission("denied");
      },
      { timeout: 10000 },
    );
  }, []);

  return { requestLocation };
}
