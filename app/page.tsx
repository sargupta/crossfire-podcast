'use client';

import PodcastPlayer from '@/components/PodcastPlayer';

export default function Home() {
  return (
    <main className="h-screen w-screen overflow-hidden bg-black">
      <PodcastPlayer initialTopic="Future of Artificial Intelligence" />
    </main>
  );
}
