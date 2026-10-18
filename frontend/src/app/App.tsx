
import { Route, Routes } from "react-router";

import Navbar from "../components/navbar/Navbar";
import HomePage from "../pages/HomePage";
import ExplorerDataPage from "../pages/ExplorerDataPage";
import IndicatorDetailPage from "../pages/IndicatorDetailPage";
import IndicatorChangesPage from "../pages/IndicatorChangesPage";
import IndicatorObservationsPage from "../pages/IndicatorObservationsPage";
import PopulationPage from "../pages/PopulationPage";

function App() {
  return (
    <>
      <Navbar />

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/explore" element={<ExplorerDataPage />} />

        <Route
          path="/indicators/:code/changes"
          element={<IndicatorChangesPage />}
        />

        <Route
          path="/indicators/:code/observations"
          element={<IndicatorObservationsPage />}
        />

        <Route
          path="/indicators/:code"
          element={<IndicatorDetailPage />}
        />
        <Route path="/population" element={<PopulationPage />} />
      </Routes>
    </>
  );
}

export default App;
