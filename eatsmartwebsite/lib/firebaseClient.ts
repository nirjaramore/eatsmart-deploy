import { initializeApp } from 'firebase/app'
import { getStorage, ref as storageRef, uploadBytesResumable, getDownloadURL } from 'firebase/storage'
import { getFirestore, collection, query, where, onSnapshot } from 'firebase/firestore'

// Use your web config (replace with your actual values if different)
const firebaseConfig = {
    apiKey: 'AIzaSyCRF6Lziwv6JhJAwOg2f44BuUAcrnTE-0E',
    authDomain: 'eatsmartly-4d8d1.firebaseapp.com',
    projectId: 'eatsmartly-4d8d1',
    storageBucket: 'eatsmartly-4d8d1.firebasestorage.app',
    messagingSenderId: '523410830428',
    appId: '1:523410830428:web:47b41d85265ae5c374a299',
    measurementId: 'G-7LR5NMZZGX'
}

const app = initializeApp(firebaseConfig)
export const storage = getStorage(app)
export const firestore = getFirestore(app)

export async function uploadFileWithProgress(path: string, file: File, onProgress?: (percent: number) => void) {
    const ref = storageRef(storage, path)
    const task = uploadBytesResumable(ref, file)

    return new Promise<string>((resolve, reject) => {
        task.on('state_changed', (snap) => {
            const percent = Math.round((snap.bytesTransferred / snap.totalBytes) * 100)
            onProgress?.(percent)
        }, (err) => reject(err), async () => {
            try {
                const url = await getDownloadURL(ref)
                resolve(url)
            } catch (e) {
                reject(e)
            }
        })
    })
}

export function listenForProductBySourcePath(path: string, cb: (docs: any[]) => void) {
    const q = query(collection(firestore, 'products'), where('sourcePath', '==', path))
    return onSnapshot(q, (snap) => {
        const docs: any[] = []
        snap.forEach((d) => docs.push({ id: d.id, ...d.data() }))
        cb(docs)
    })
}
