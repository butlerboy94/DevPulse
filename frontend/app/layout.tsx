// Root layout — wraps every page in the app. Mounts the Navbar once here so
// it doesn't need to be re-added to each page, and sets the browser tab
// title/description.
import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "DevPulse — Code Performance Analysis",
  description: "Paste your code and get a full performance analysis powered by C++ and AI.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
